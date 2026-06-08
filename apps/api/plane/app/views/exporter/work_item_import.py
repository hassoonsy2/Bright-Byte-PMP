# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import json
import re

# Third party imports
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

# Module imports
from plane.app.permissions import ROLE, allow_permission
from plane.db.models import Issue, IssueLabel, Label, Project, State, Workspace

from .. import BaseAPIView

PRIORITIES = {"urgent", "high", "medium", "low", "none"}
MAX_ROWS = 2000


def parse_duration_to_seconds(value):
    """Mirror of the frontend parseDurationToSeconds.

    Bare number -> minutes; h/m/s unit tokens; decimals via dot or comma.
    Returns whole seconds, or None when empty/invalid.
    """
    if value is None:
        return None
    text = str(value).strip().lower().replace(",", ".")
    if text == "":
        return None
    if re.fullmatch(r"\d*\.?\d+", text):
        return round(float(text) * 60)
    total = 0.0
    matched = False
    for match in re.finditer(r"(\d*\.?\d+)\s*(h|m|s)", text):
        amount = float(match.group(1))
        matched = True
        unit = match.group(2)
        total += amount * 3600 if unit == "h" else amount * 60 if unit == "m" else amount
    return round(total) if matched else None


def parse_date(value):
    if not value:
        return None
    text = str(value).strip()
    return text[:10] or None


def parse_labels(value):
    if not value:
        return []
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("["):
            try:
                return [str(item).strip() for item in json.loads(text) if str(item).strip()]
            except (ValueError, TypeError):
                pass
        return [part.strip() for part in text.split(",") if part.strip()]
    return []


class WorkItemImportEndpoint(BaseAPIView):
    """Import work items into a project from an uploaded CSV or XLSX file.

    Accepts the same column layout that the work-item export produces (extra
    columns are ignored), so an export can be re-imported. Recognised columns
    (header names, case/spacing-insensitive): Name (required), Description,
    State Name, Priority, Start Date, Target Date, Duration, Estimate Time, Labels.
    """

    parser_classes = (MultiPartParser, FormParser)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="PROJECT")
    def post(self, request, slug, project_id):
        upload = request.FILES.get("file")
        if not upload:
            return Response(
                {"error": "No file uploaded. Attach a CSV or XLSX file in the 'file' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Lazy import to avoid loading the formatters unless an import is requested
        from plane.utils.porters.formatters import CSVFormatter, XLSXFormatter

        filename = (upload.name or "").lower()
        content = upload.read()
        try:
            if filename.endswith(".xlsx"):
                rows = XLSXFormatter().decode(content)
            else:
                text = content.decode("utf-8-sig") if isinstance(content, bytes) else content
                rows = CSVFormatter().decode(text)
        except Exception as exc:  # noqa: BLE001 - surface a friendly parse error
            return Response(
                {"error": f"Could not parse the file: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not rows:
            return Response({"error": "The file has no data rows."}, status=status.HTTP_400_BAD_REQUEST)
        if len(rows) > MAX_ROWS:
            return Response(
                {"error": f"Too many rows ({len(rows)}). Import at most {MAX_ROWS} work items at a time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workspace = Workspace.objects.get(slug=slug)
        project = Project.objects.get(pk=project_id, workspace=workspace)

        states = {state.name.strip().lower(): state for state in State.objects.filter(project=project)}
        default_state = next((state for state in states.values() if state.default), None) or next(
            iter(states.values()), None
        )
        labels = {label.name.strip().lower(): label for label in Label.objects.filter(project=project)}

        created, failed, errors = 0, 0, []

        for index, row in enumerate(rows, start=2):  # row 1 is the header
            title = (row.get("name") or "").strip()
            if not title:
                continue
            try:
                state = states.get((row.get("state_name") or "").strip().lower()) or default_state
                priority = (row.get("priority") or "none").strip().lower()
                if priority not in PRIORITIES:
                    priority = "none"

                issue = Issue.objects.create(
                    name=title[:255],
                    project=project,
                    workspace=workspace,
                    state=state,
                    priority=priority,
                    start_date=parse_date(row.get("start_date")),
                    target_date=parse_date(row.get("target_date")),
                    duration=parse_duration_to_seconds(row.get("duration")),
                    estimate_time=parse_duration_to_seconds(row.get("estimate_time")),
                    created_by=request.user,
                    updated_by=request.user,
                )

                description = row.get("description_html") or row.get("description")
                if description:
                    issue.description_html = str(description)
                    issue.save(update_fields=["description_html", "description_stripped"])

                for label_name in parse_labels(row.get("labels")):
                    key = label_name.strip().lower()
                    label = labels.get(key)
                    if not label:
                        label = Label.objects.create(
                            name=label_name[:255],
                            project=project,
                            workspace=workspace,
                            created_by=request.user,
                            updated_by=request.user,
                        )
                        labels[key] = label
                    IssueLabel.objects.get_or_create(
                        issue=issue,
                        label=label,
                        project=project,
                        workspace=workspace,
                        defaults={"created_by": request.user, "updated_by": request.user},
                    )

                created += 1
            except Exception as exc:  # noqa: BLE001 - collect per-row failures, keep importing
                failed += 1
                if len(errors) < 25:
                    errors.append({"row": index, "name": title[:80], "error": str(exc)[:200]})

        return Response(
            {"created": created, "failed": failed, "total": created + failed, "errors": errors},
            status=status.HTTP_200_OK,
        )
