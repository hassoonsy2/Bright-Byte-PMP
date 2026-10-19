# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for the per-project Slack notification helpers (no database needed)."""

from unittest import mock

import pytest
import requests

from plane.settings.common import _parse_slug_allowlist
from plane.utils.slack_notification import (
    build_change_lines,
    build_issue_url,
    build_slack_payload,
    escape_slack_text,
    is_valid_slack_webhook_url,
    is_workspace_allowlisted,
    mask_webhook_url,
    post_to_slack,
)

VALID_URL = "https://hooks.slack.com/services/T000/B000/abcdWXYZ"
ALL_ON = {
    "notify_issue_created": True,
    "notify_state_changed": True,
    "notify_assignee_changed": True,
    "notify_priority_changed": True,
    "notify_comment_created": True,
    "notify_issue_deleted": True,
}


def _activity(verb="updated", field=None, old_value=None, new_value=None):
    return {"verb": verb, "field": field, "old_value": old_value, "new_value": new_value}


def _response(status_code, text="", headers=None):
    response = mock.Mock()
    response.status_code = status_code
    response.text = text
    response.headers = headers or {}
    return response


@pytest.mark.unit
class TestWebhookUrlValidation:
    def test_accepts_slack_incoming_webhook(self):
        assert is_valid_slack_webhook_url(VALID_URL)

    @pytest.mark.parametrize(
        "url",
        [
            "http://hooks.slack.com/services/T000/B000/XXXX",
            "https://hooks.slack.com.evil.com/services/T000/B000/XXXX",
            "https://evil.com/?https://hooks.slack.com/services/x",
            "https://user@hooks.slack.com/services/x",
            "https://hooks.slack.com:8443/services/x",
            "https://hooks.slack.com/services/",
            "https://hooks.slack.com/services/T000/B000/XX XX",
            "https://hooks.slack.com/services/T000/B000/XXXX?redirect=1",
            "https://hooks.slack.com/services/T000/B000/XXXX#frag",
            "",
            None,
            123,
        ],
    )
    def test_rejects_everything_else(self, url):
        assert not is_valid_slack_webhook_url(url)


@pytest.mark.unit
class TestMaskWebhookUrl:
    def test_keeps_only_last_four_characters(self):
        masked = mask_webhook_url(VALID_URL)
        assert masked == "https://hooks.slack.com/services/…/WXYZ"
        assert "T000" not in masked
        assert "B000" not in masked

    def test_empty(self):
        assert mask_webhook_url("") == ""
        assert mask_webhook_url(None) == ""


@pytest.mark.unit
class TestWorkspaceAllowlist:
    def test_parse_slug_allowlist(self):
        assert _parse_slug_allowlist(" Ambis, ,foo,ambis ") == ["ambis", "foo"]
        assert _parse_slug_allowlist("") == []
        assert _parse_slug_allowlist(None) == []

    def test_allowlisted_workspace(self, settings):
        settings.SLACK_NOTIFICATION_WORKSPACES = ["ambis"]
        assert is_workspace_allowlisted("ambis")
        assert is_workspace_allowlisted(" AMBIS ")
        assert not is_workspace_allowlisted("other")
        assert not is_workspace_allowlisted(None)
        assert not is_workspace_allowlisted("")

    def test_empty_allowlist_disables_everywhere(self, settings):
        settings.SLACK_NOTIFICATION_WORKSPACES = []
        assert not is_workspace_allowlisted("ambis")


@pytest.mark.unit
class TestEscapeSlackText:
    def test_escapes_control_characters(self):
        assert escape_slack_text("a & <b>") == "a &amp; &lt;b&gt;"

    def test_none(self):
        assert escape_slack_text(None) == ""


@pytest.mark.unit
class TestBuildChangeLines:
    def test_state_change(self):
        lines = build_change_lines(
            "issue.activity.updated",
            [_activity(field="state", old_value="Todo", new_value="In Progress")],
            ALL_ON,
        )
        assert lines == ["State: Todo → In Progress"]

    def test_state_with_missing_side(self):
        lines = build_change_lines(
            "issue.activity.updated", [_activity(field="state", old_value=None, new_value="Done")], ALL_ON
        )
        assert lines == ["State: — → Done"]

    def test_assignees(self):
        lines = build_change_lines(
            "issue.activity.updated",
            [
                _activity(field="assignees", old_value="", new_value="Jane"),
                _activity(field="assignees", old_value="Bob", new_value=""),
            ],
            ALL_ON,
        )
        assert lines == ["Assigned: Jane", "Unassigned: Bob"]

    def test_priority(self):
        lines = build_change_lines(
            "issue.activity.updated", [_activity(field="priority", old_value=None, new_value="high")], ALL_ON
        )
        assert lines == ["Priority: none → high"]

    def test_comment_html_is_flattened(self):
        lines = build_change_lines(
            "comment.activity.created",
            [_activity(verb="created", field="comment", new_value="<p>Hello <b>team</b> &amp; co</p>")],
            ALL_ON,
        )
        assert lines == ["Comment: Hello team &amp; co"]

    def test_long_comment_is_truncated(self):
        lines = build_change_lines(
            "comment.activity.created",
            [_activity(verb="created", field="comment", new_value="x" * 1000)],
            ALL_ON,
        )
        assert lines == ["Comment: " + "x" * 300 + "…"]

    def test_deleted(self):
        lines = build_change_lines("issue.activity.deleted", [_activity(verb="deleted", field="issue")], ALL_ON)
        assert lines == ["Deleted"]

    def test_created_without_activities(self):
        assert build_change_lines("issue.activity.created", [], ALL_ON) == ["Created"]

    def test_created_with_assignee(self):
        lines = build_change_lines(
            "issue.activity.created",
            [_activity(field="assignees", old_value="", new_value="Jane")],
            ALL_ON,
        )
        assert lines == ["Created", "Assigned: Jane"]

    def test_values_are_escaped(self):
        lines = build_change_lines(
            "issue.activity.updated",
            [_activity(field="state", old_value="<b>", new_value="A & B")],
            ALL_ON,
        )
        assert lines == ["State: &lt;b&gt; → A &amp; B"]

    @pytest.mark.parametrize(
        "toggle,event_type,activity",
        [
            ("notify_state_changed", "issue.activity.updated", _activity(field="state", new_value="Done")),
            ("notify_assignee_changed", "issue.activity.updated", _activity(field="assignees", new_value="Jane")),
            ("notify_priority_changed", "issue.activity.updated", _activity(field="priority", new_value="high")),
            (
                "notify_comment_created",
                "comment.activity.created",
                _activity(verb="created", field="comment", new_value="hi"),
            ),
            ("notify_issue_deleted", "issue.activity.deleted", _activity(verb="deleted", field="issue")),
            ("notify_issue_created", "issue.activity.created", _activity(verb="created")),
        ],
    )
    def test_toggle_off_suppresses_line(self, toggle, event_type, activity):
        assert build_change_lines(event_type, [activity], {**ALL_ON, toggle: False}) == []

    @pytest.mark.parametrize("field", ["labels", "name", "description", "target_date"])
    def test_other_fields_are_ignored(self, field):
        lines = build_change_lines(
            "issue.activity.updated", [_activity(field=field, old_value="a", new_value="b")], ALL_ON
        )
        assert lines == []


@pytest.mark.unit
class TestBuildSlackPayload:
    def test_payload_with_link(self):
        url = build_issue_url("https://pmp.example.com/", "ambis", "AMB", 12)
        assert url == "https://pmp.example.com/ambis/browse/AMB-12/"
        payload = build_slack_payload(
            issue_label="AMB-12 Fix <login>",
            issue_url=url,
            project_name="Ambis Intern",
            actor_name="Jane",
            lines=["State: Todo → Done"],
        )
        assert payload["text"]
        assert isinstance(payload["blocks"], list)
        assert (
            "<https://pmp.example.com/ambis/browse/AMB-12/|AMB-12 Fix &lt;login&gt;>"
            in (payload["blocks"][0]["text"]["text"])
        )
        context = payload["blocks"][-1]["elements"][0]["text"]
        assert "Ambis Intern" in context
        assert "Jane" in context

    def test_payload_without_base_url(self):
        assert build_issue_url(None, "ambis", "AMB", 12) is None
        payload = build_slack_payload(
            issue_label="AMB-12 Fix login",
            issue_url=None,
            project_name="Ambis",
            actor_name="Jane",
            lines=["Created"],
        )
        assert "<http" not in str(payload)


@pytest.mark.unit
class TestPostToSlack:
    def test_success(self):
        with mock.patch("plane.utils.slack_notification.requests.post", return_value=_response(200, "ok")) as post:
            result = post_to_slack(VALID_URL, {"text": "hi"})
        assert result.ok
        assert post.call_args.kwargs["timeout"] == 10
        assert post.call_args.kwargs["allow_redirects"] is False

    def test_rate_limited_is_retryable(self):
        response = _response(429, "rate_limited", {"Retry-After": "7"})
        with mock.patch("plane.utils.slack_notification.requests.post", return_value=response):
            result = post_to_slack(VALID_URL, {"text": "hi"})
        assert not result.ok
        assert result.retryable
        assert result.retry_after == 7

    def test_client_error_is_not_retryable(self):
        with mock.patch("plane.utils.slack_notification.requests.post", return_value=_response(404, "no_service")):
            result = post_to_slack(VALID_URL, {"text": "hi"})
        assert not result.ok
        assert not result.retryable
        assert "no_service" in result.error

    def test_server_error_is_retryable(self):
        with mock.patch("plane.utils.slack_notification.requests.post", return_value=_response(503)):
            result = post_to_slack(VALID_URL, {"text": "hi"})
        assert result.retryable

    def test_network_error_never_leaks_url(self):
        error = requests.ConnectionError(f"Max retries exceeded with url: {VALID_URL}")
        with mock.patch("plane.utils.slack_notification.requests.post", side_effect=error):
            result = post_to_slack(VALID_URL, {"text": "hi"})
        assert not result.ok
        assert result.retryable
        assert result.error == "ConnectionError"
        assert "hooks.slack.com/services" not in result.error

    def test_invalid_url_is_never_requested(self):
        with mock.patch("plane.utils.slack_notification.requests.post") as post:
            result = post_to_slack("https://evil.com/hook", {"text": "hi"})
        post.assert_not_called()
        assert not result.ok
        assert not result.retryable
