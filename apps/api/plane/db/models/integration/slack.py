# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports

# Django imports
from django.db import models

# Module imports
from plane.db.models.project import ProjectBaseModel


class SlackProjectSync(ProjectBaseModel):
    access_token = models.CharField(max_length=300)
    scopes = models.TextField()
    bot_user_id = models.CharField(max_length=50)
    webhook_url = models.URLField(max_length=1000)
    data = models.JSONField(default=dict)
    team_id = models.CharField(max_length=30)
    team_name = models.CharField(max_length=300)
    workspace_integration = models.ForeignKey(
        "db.WorkspaceIntegration", related_name="slack_syncs", on_delete=models.CASCADE
    )

    def __str__(self):
        """Return the repo name"""
        return f"{self.project.name}"

    class Meta:
        unique_together = ["team_id", "project"]
        verbose_name = "Slack Project Sync"
        verbose_name_plural = "Slack Project Syncs"
        db_table = "slack_project_syncs"
        ordering = ("-created_at",)


class ProjectSlackNotification(ProjectBaseModel):
    # Fernet ciphertext of the Slack incoming-webhook URL (the URL itself is a secret)
    webhook_url = models.TextField()
    is_active = models.BooleanField(default=True)
    notify_issue_created = models.BooleanField(default=True)
    notify_state_changed = models.BooleanField(default=True)
    notify_assignee_changed = models.BooleanField(default=True)
    notify_priority_changed = models.BooleanField(default=True)
    notify_comment_created = models.BooleanField(default=True)
    notify_issue_deleted = models.BooleanField(default=True)
    last_delivered_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.project.name}"

    class Meta:
        verbose_name = "Project Slack Notification"
        verbose_name_plural = "Project Slack Notifications"
        db_table = "project_slack_notifications"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["project"],
                condition=models.Q(deleted_at__isnull=True),
                name="project_slack_notification_unique_project_when_deleted_at_null",
            )
        ]
