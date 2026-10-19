# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Helpers for per-project Slack notifications.

Kept free of model imports so the URL checks and message formatting can be
unit-tested without a database.
"""

# Python imports
import html
import re
from typing import NamedTuple, Optional
from urllib.parse import urlparse

# Third party imports
import requests

# Django imports
from django.conf import settings
from django.utils.html import strip_tags

SLACK_WEBHOOK_PREFIX = "https://hooks.slack.com/services/"
SLACK_NOTIFICATION_TOGGLE_FIELDS = (
    "notify_issue_created",
    "notify_state_changed",
    "notify_assignee_changed",
    "notify_priority_changed",
    "notify_comment_created",
    "notify_issue_deleted",
)
SLACK_NOTIFICATION_EVENT_TYPES = frozenset(
    {
        "issue.activity.created",
        "issue.activity.updated",
        "issue.activity.deleted",
        "comment.activity.created",
    }
)
SLACK_REQUEST_TIMEOUT = 10
MAX_ERROR_LENGTH = 500


def is_valid_slack_webhook_url(url):
    """Only Slack incoming-webhook URLs are accepted, which rules out SSRF to any other host."""
    if not isinstance(url, str) or not url or len(url) > 1024:
        return False
    if any(char.isspace() for char in url):
        return False
    if not url.startswith(SLACK_WEBHOOK_PREFIX) or not url[len(SLACK_WEBHOOK_PREFIX) :].strip("/"):
        return False
    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and parsed.hostname == "hooks.slack.com"
        and port is None
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
    )


def mask_webhook_url(url):
    """Show only the last four characters of the secret webhook path."""
    if not url:
        return ""
    return f"{SLACK_WEBHOOK_PREFIX}…/{url[-4:]}"


def is_workspace_allowlisted(slug):
    if not slug:
        return False
    return slug.strip().lower() in getattr(settings, "SLACK_NOTIFICATION_WORKSPACES", [])


def escape_slack_text(value):
    """Escape the three characters Slack treats as control characters in mrkdwn."""
    return str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_web_base_url():
    # APP_BASE_URL is the web app; on Render WEB_URL points at the API host.
    base_url = getattr(settings, "APP_BASE_URL", None) or getattr(settings, "WEB_URL", None)
    return base_url.rstrip("/") if base_url else None


class SlackDeliveryResult(NamedTuple):
    ok: bool
    status_code: Optional[int] = None
    error: str = ""
    retry_after: Optional[int] = None
    invalid: bool = False

    @property
    def retryable(self):
        if self.ok or self.invalid:
            return False
        return self.status_code is None or self.status_code == 429 or self.status_code >= 500


def post_to_slack(webhook_url, payload):
    if not is_valid_slack_webhook_url(webhook_url):
        return SlackDeliveryResult(ok=False, error="Invalid Slack webhook URL", invalid=True)

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=SLACK_REQUEST_TIMEOUT,
            allow_redirects=False,
        )
    except requests.RequestException as e:
        # requests embeds the URL (the secret) in exception messages, so keep only the class name
        return SlackDeliveryResult(ok=False, error=type(e).__name__[:MAX_ERROR_LENGTH])

    if response.status_code == 200:
        return SlackDeliveryResult(ok=True, status_code=200)

    retry_after = response.headers.get("Retry-After")
    return SlackDeliveryResult(
        ok=False,
        status_code=response.status_code,
        error=f"HTTP {response.status_code}: {response.text[:200]}"[:MAX_ERROR_LENGTH],
        retry_after=int(retry_after) if retry_after and retry_after.isdigit() else None,
    )


def build_test_payload(project_name, actor_name):
    project = escape_slack_text(project_name)
    actor = escape_slack_text(actor_name)
    return {
        "text": f"Slack notifications are connected for {project}.",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":white_check_mark: Slack notifications are connected for *{project}*.",
                },
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Test message sent by {actor} from Bright-Byte PMP"}],
            },
        ],
    }


def html_to_plain_text(value, limit=300):
    text = re.sub(r"\s+", " ", html.unescape(strip_tags(value or ""))).strip()
    if len(text) > limit:
        return text[:limit] + "…"
    return text


def describe_activity(activity, toggles):
    """Turn one IssueActivity-shaped dict into a single human-readable line, or None to skip it."""
    verb = activity.get("verb")
    field = activity.get("field")
    old_value = activity.get("old_value")
    new_value = activity.get("new_value")

    if field == "state" and verb == "updated" and toggles.get("notify_state_changed", True):
        return f"State: {escape_slack_text(old_value or '—')} → {escape_slack_text(new_value or '—')}"
    if field == "assignees" and toggles.get("notify_assignee_changed", True):
        if new_value:
            return f"Assigned: {escape_slack_text(new_value)}"
        if old_value:
            return f"Unassigned: {escape_slack_text(old_value)}"
        return None
    if field == "priority" and toggles.get("notify_priority_changed", True):
        return f"Priority: {escape_slack_text(old_value or 'none')} → {escape_slack_text(new_value or 'none')}"
    if field == "comment" and verb == "created" and toggles.get("notify_comment_created", True):
        return f"Comment: {escape_slack_text(html_to_plain_text(new_value))}"
    if field == "issue" and verb == "deleted" and toggles.get("notify_issue_deleted", True):
        return "Deleted"
    if verb == "created" and not field and toggles.get("notify_issue_created", True):
        return "Created"
    return None


def build_change_lines(event_type, activities, toggles):
    lines = []
    # The "created" activity is written outside the bulk-created list, so add it from the event type
    if event_type == "issue.activity.created" and toggles.get("notify_issue_created", True):
        lines.append("Created")
    for activity in activities:
        line = describe_activity(activity, toggles)
        if line and line not in lines:
            lines.append(line)
    return lines


def build_issue_url(base_url, workspace_slug, project_identifier, sequence_id):
    if not base_url:
        return None
    return f"{base_url.rstrip('/')}/{workspace_slug}/browse/{project_identifier}-{sequence_id}/"


def build_slack_payload(*, issue_label, issue_url, project_name, actor_name, lines):
    label = escape_slack_text(issue_label)
    project = escape_slack_text(project_name)
    actor = escape_slack_text(actor_name)
    title = f"<{issue_url}|{label}>" if issue_url else label
    return {
        "text": f"{label} ({project}): {'; '.join(lines)} — by {actor}"[:3000],
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "\n".join(f"• {line}" for line in lines)[:2900]},
            },
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"{project} · by {actor}"}]},
        ],
    }
