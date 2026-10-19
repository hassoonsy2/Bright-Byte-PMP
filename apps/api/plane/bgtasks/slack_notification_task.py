# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import logging

# Third party imports
from celery import shared_task

# Django imports
from django.utils import timezone

# Module imports
from plane.db.models import Issue, IssueActivity, Project, ProjectSlackNotification, User
from plane.license.utils.encryption import decrypt_data
from plane.utils.exception_logger import log_exception
from plane.utils.slack_notification import (
    MAX_ERROR_LENGTH,
    SLACK_NOTIFICATION_EVENT_TYPES,
    SLACK_NOTIFICATION_TOGGLE_FIELDS,
    build_change_lines,
    build_issue_url,
    build_slack_payload,
    get_web_base_url,
    is_workspace_allowlisted,
    post_to_slack,
)

logger = logging.getLogger("plane.worker")


def _build_notification(event_type, project_id, issue_id, actor_id, activity_ids):
    """Return (config, payload) for one work-item action, or None when nothing should be sent."""
    if event_type not in SLACK_NOTIFICATION_EVENT_TYPES or not issue_id:
        return None

    project = Project.objects.select_related("workspace").filter(pk=project_id).first()
    if project is None or not is_workspace_allowlisted(project.workspace.slug):
        return None

    config = ProjectSlackNotification.objects.filter(project_id=project_id, is_active=True).first()
    if config is None:
        return None

    # all_objects so a deleted work item still resolves
    issue = Issue.all_objects.filter(pk=issue_id).first()
    if issue is None or issue.is_draft:
        return None

    activities = [
        {
            "verb": activity.verb,
            "field": activity.field,
            "old_value": activity.old_value,
            "new_value": activity.new_value,
        }
        for activity in IssueActivity.objects.filter(pk__in=activity_ids or []).order_by("created_at")
    ]
    toggles = {field: getattr(config, field) for field in SLACK_NOTIFICATION_TOGGLE_FIELDS}
    lines = build_change_lines(event_type, activities, toggles)
    if not lines:
        return None

    actor = User.objects.filter(pk=actor_id).first() if actor_id else None
    actor_name = (actor.display_name or actor.first_name) if actor else ""

    payload = build_slack_payload(
        issue_label=f"{project.identifier}-{issue.sequence_id} {issue.name}",
        issue_url=build_issue_url(get_web_base_url(), project.workspace.slug, project.identifier, issue.sequence_id),
        project_name=project.name,
        actor_name=actor_name or "Someone",
        lines=lines,
    )
    return config, payload


@shared_task(bind=True, max_retries=2)
def send_slack_notification(self, event_type, project_id, issue_id, actor_id, activity_ids):
    try:
        notification = _build_notification(event_type, project_id, issue_id, actor_id, activity_ids)
    except Exception as e:
        log_exception(e)
        return

    if notification is None:
        return

    config, payload = notification
    result = post_to_slack(decrypt_data(config.webhook_url), payload)

    if result.ok:
        ProjectSlackNotification.objects.filter(pk=config.pk).update(last_delivered_at=timezone.now(), last_error="")
        return

    # Kept outside any broad except so Celery's Retry exception propagates
    if result.retryable and self.request.retries < self.max_retries:
        raise self.retry(countdown=min(result.retry_after or 30, 300))

    ProjectSlackNotification.objects.filter(pk=config.pk).update(last_error=result.error[:MAX_ERROR_LENGTH])
    logger.warning(
        "Slack notification failed for project %s (status %s)",
        project_id,
        result.status_code,
    )
