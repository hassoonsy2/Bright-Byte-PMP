# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
from functools import wraps

# Django imports
from django.db import IntegrityError
from django.utils import timezone

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.permissions import allow_permission, ROLE
from plane.db.models import Project, ProjectSlackNotification
from plane.license.utils.encryption import decrypt_data, encrypt_data
from plane.utils.slack_notification import (
    MAX_ERROR_LENGTH,
    SLACK_NOTIFICATION_TOGGLE_FIELDS,
    build_test_payload,
    is_valid_slack_webhook_url,
    is_workspace_allowlisted,
    mask_webhook_url,
    post_to_slack,
)
from ..base import BaseAPIView


def slack_notifications_enabled(view_func):
    """Answer 404 for workspaces outside SLACK_NOTIFICATION_WORKSPACES, before any permission check."""

    @wraps(view_func)
    def _wrapped_view(instance, request, *args, **kwargs):
        if not is_workspace_allowlisted(kwargs.get("slug")):
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return view_func(instance, request, *args, **kwargs)

    return _wrapped_view


def _serialize(config, project_id):
    if config is None:
        return {
            "id": None,
            "project_id": str(project_id),
            "has_webhook_url": False,
            "webhook_url_masked": "",
            "is_active": True,
            **{field: True for field in SLACK_NOTIFICATION_TOGGLE_FIELDS},
            "last_delivered_at": None,
            "last_error": "",
        }

    return {
        "id": str(config.id),
        "project_id": str(project_id),
        "has_webhook_url": bool(config.webhook_url),
        "webhook_url_masked": mask_webhook_url(decrypt_data(config.webhook_url)),
        "is_active": config.is_active,
        **{field: getattr(config, field) for field in SLACK_NOTIFICATION_TOGGLE_FIELDS},
        "last_delivered_at": config.last_delivered_at.isoformat() if config.last_delivered_at else None,
        "last_error": config.last_error,
    }


def _get_config(slug, project_id):
    return ProjectSlackNotification.objects.filter(project_id=project_id, workspace__slug=slug).first()


class ProjectSlackNotificationEndpoint(BaseAPIView):
    @slack_notifications_enabled
    @allow_permission(allowed_roles=[ROLE.ADMIN])
    def get(self, request, slug, project_id):
        return Response(_serialize(_get_config(slug, project_id), project_id), status=status.HTTP_200_OK)

    @slack_notifications_enabled
    @allow_permission(allowed_roles=[ROLE.ADMIN])
    def patch(self, request, slug, project_id):
        data = request.data
        if not isinstance(data, dict):
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        config = _get_config(slug, project_id)

        encrypted_url = None
        webhook_url = data.get("webhook_url")
        if isinstance(webhook_url, str) and webhook_url.strip():
            webhook_url = webhook_url.strip()
            if not is_valid_slack_webhook_url(webhook_url):
                return Response(
                    {"error": "Webhook URL must start with https://hooks.slack.com/services/"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            encrypted_url = encrypt_data(webhook_url)
            if not encrypted_url:
                return Response(
                    {"error": "Could not store webhook URL"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        elif webhook_url not in (None, ""):
            return Response({"error": "webhook_url must be a string"}, status=status.HTTP_400_BAD_REQUEST)

        if config is None and encrypted_url is None:
            return Response({"error": "webhook_url is required"}, status=status.HTTP_400_BAD_REQUEST)

        flags = {}
        for field in ("is_active", *SLACK_NOTIFICATION_TOGGLE_FIELDS):
            if field in data:
                if not isinstance(data[field], bool):
                    return Response({"error": f"{field} must be a boolean"}, status=status.HTTP_400_BAD_REQUEST)
                flags[field] = data[field]

        if config is None:
            project = Project.objects.get(pk=project_id, workspace__slug=slug)
            config = ProjectSlackNotification(project=project)

        if encrypted_url is not None:
            config.webhook_url = encrypted_url
            config.last_error = ""
        for field, value in flags.items():
            setattr(config, field, value)

        try:
            config.save()
        except IntegrityError:
            return Response(
                {"error": "Slack notifications are already configured for this project"},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(_serialize(config, project_id), status=status.HTTP_200_OK)

    @slack_notifications_enabled
    @allow_permission(allowed_roles=[ROLE.ADMIN])
    def delete(self, request, slug, project_id):
        config = _get_config(slug, project_id)
        if config is not None:
            # Hard delete so the encrypted webhook URL is not retained
            config.delete(soft=False)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectSlackNotificationTestEndpoint(BaseAPIView):
    @slack_notifications_enabled
    @allow_permission(allowed_roles=[ROLE.ADMIN])
    def post(self, request, slug, project_id):
        config = _get_config(slug, project_id)
        if config is None or not config.webhook_url:
            return Response(
                {"success": False, "error": "Save a Slack webhook URL first"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = build_test_payload(config.project.name, request.user.display_name)
        result = post_to_slack(decrypt_data(config.webhook_url), payload)

        if result.ok:
            ProjectSlackNotification.objects.filter(pk=config.pk).update(
                last_delivered_at=timezone.now(), last_error=""
            )
            return Response({"success": True}, status=status.HTTP_200_OK)

        ProjectSlackNotification.objects.filter(pk=config.pk).update(last_error=result.error[:MAX_ERROR_LENGTH])
        return Response({"success": False, "error": result.error}, status=status.HTTP_400_BAD_REQUEST)
