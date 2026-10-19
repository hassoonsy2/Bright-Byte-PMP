# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for the Slack notification hook and Celery task (database calls are mocked)."""

from types import SimpleNamespace
from unittest import mock

import pytest
from celery.exceptions import Retry

from plane.bgtasks import issue_activities_task, slack_notification_task
from plane.utils.slack_notification import SlackDeliveryResult

PROJECT_ID = "11111111-1111-1111-1111-111111111111"
ISSUE_ID = "22222222-2222-2222-2222-222222222222"
ACTOR_ID = "33333333-3333-3333-3333-333333333333"


def _project(slug="ambis"):
    return SimpleNamespace(id=PROJECT_ID, workspace=SimpleNamespace(slug=slug))


def _activities(count=1):
    return [SimpleNamespace(id=f"00000000-0000-0000-0000-00000000000{i}") for i in range(count)]


@pytest.mark.unit
class TestEnqueueSlackNotification:
    @pytest.fixture
    def delay(self):
        with mock.patch.object(issue_activities_task.send_slack_notification, "delay") as delay:
            yield delay

    @pytest.fixture
    def config_exists(self):
        with mock.patch.object(issue_activities_task.ProjectSlackNotification, "objects") as objects:
            objects.filter.return_value.exists.return_value = True
            yield objects

    def test_feature_off_makes_no_queries(self, settings, delay, config_exists):
        settings.SLACK_NOTIFICATION_WORKSPACES = []
        issue_activities_task._enqueue_slack_notification(
            "issue.activity.updated", _project(), ISSUE_ID, ACTOR_ID, _activities()
        )
        config_exists.filter.assert_not_called()
        delay.assert_not_called()

    def test_other_workspace_is_ignored(self, settings, delay, config_exists):
        settings.SLACK_NOTIFICATION_WORKSPACES = ["ambis"]
        issue_activities_task._enqueue_slack_notification(
            "issue.activity.updated", _project("other"), ISSUE_ID, ACTOR_ID, _activities()
        )
        delay.assert_not_called()

    def test_unrelated_event_type_is_ignored(self, settings, delay, config_exists):
        settings.SLACK_NOTIFICATION_WORKSPACES = ["ambis"]
        issue_activities_task._enqueue_slack_notification(
            "link.activity.created", _project(), ISSUE_ID, ACTOR_ID, _activities()
        )
        delay.assert_not_called()

    def test_inactive_or_missing_config_is_ignored(self, settings, delay, config_exists):
        settings.SLACK_NOTIFICATION_WORKSPACES = ["ambis"]
        config_exists.filter.return_value.exists.return_value = False
        issue_activities_task._enqueue_slack_notification(
            "issue.activity.updated", _project(), ISSUE_ID, ACTOR_ID, _activities()
        )
        delay.assert_not_called()

    def test_enqueues_for_allowlisted_project(self, settings, delay, config_exists):
        settings.SLACK_NOTIFICATION_WORKSPACES = ["ambis"]
        activities = _activities(2)
        issue_activities_task._enqueue_slack_notification(
            "issue.activity.updated", _project(), ISSUE_ID, ACTOR_ID, activities
        )
        delay.assert_called_once_with(
            event_type="issue.activity.updated",
            project_id=PROJECT_ID,
            issue_id=ISSUE_ID,
            actor_id=ACTOR_ID,
            activity_ids=[str(a.id) for a in activities],
        )

    def test_created_event_enqueues_without_bulk_activities(self, settings, delay, config_exists):
        settings.SLACK_NOTIFICATION_WORKSPACES = ["ambis"]
        issue_activities_task._enqueue_slack_notification("issue.activity.created", _project(), ISSUE_ID, ACTOR_ID, [])
        delay.assert_called_once()

    def test_update_without_activities_is_ignored(self, settings, delay, config_exists):
        settings.SLACK_NOTIFICATION_WORKSPACES = ["ambis"]
        issue_activities_task._enqueue_slack_notification("issue.activity.updated", _project(), ISSUE_ID, ACTOR_ID, [])
        delay.assert_not_called()


@pytest.mark.unit
class TestSendSlackNotification:
    @pytest.fixture
    def notification(self):
        config = SimpleNamespace(pk="cfg", webhook_url="encrypted")
        with mock.patch.object(
            slack_notification_task, "_build_notification", return_value=(config, {"text": "hi"})
        ) as build:
            yield build

    @pytest.fixture
    def config_objects(self):
        with mock.patch.object(slack_notification_task.ProjectSlackNotification, "objects") as objects:
            yield objects

    @pytest.fixture(autouse=True)
    def decrypt(self):
        with mock.patch.object(slack_notification_task, "decrypt_data", return_value="url"):
            yield

    def _run(self):
        slack_notification_task.send_slack_notification.run(
            "issue.activity.updated", PROJECT_ID, ISSUE_ID, ACTOR_ID, ["a"]
        )

    def test_success_records_delivery(self, notification, config_objects):
        with mock.patch.object(slack_notification_task, "post_to_slack", return_value=SlackDeliveryResult(ok=True)):
            self._run()
        update_kwargs = config_objects.filter.return_value.update.call_args.kwargs
        assert update_kwargs["last_error"] == ""
        assert update_kwargs["last_delivered_at"] is not None

    def test_retryable_failure_retries(self, notification, config_objects):
        result = SlackDeliveryResult(ok=False, status_code=503, error="HTTP 503: ")
        with mock.patch.object(slack_notification_task, "post_to_slack", return_value=result):
            with pytest.raises(Retry):
                self._run()
        config_objects.filter.return_value.update.assert_not_called()

    def test_permanent_failure_records_error(self, notification, config_objects):
        result = SlackDeliveryResult(ok=False, status_code=404, error="HTTP 404: no_service")
        with mock.patch.object(slack_notification_task, "post_to_slack", return_value=result):
            self._run()
        config_objects.filter.return_value.update.assert_called_once_with(last_error="HTTP 404: no_service")

    def test_nothing_to_send(self, config_objects):
        with mock.patch.object(slack_notification_task, "_build_notification", return_value=None):
            with mock.patch.object(slack_notification_task, "post_to_slack") as post:
                self._run()
        post.assert_not_called()

    def test_build_errors_are_swallowed(self, config_objects):
        with mock.patch.object(slack_notification_task, "_build_notification", side_effect=ValueError("boom")):
            with mock.patch.object(slack_notification_task, "post_to_slack") as post:
                self._run()
        post.assert_not_called()
