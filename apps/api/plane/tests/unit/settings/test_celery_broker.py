# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for Celery broker URL env precedence."""

import pytest

from plane.settings.common import _resolve_celery_broker_url

BROKER_ENV_VARS = (
    "CELERY_BROKER_URL",
    "AMQP_URL",
    "RABBITMQ_HOST",
    "RABBITMQ_PORT",
    "RABBITMQ_USER",
    "RABBITMQ_PASSWORD",
    "RABBITMQ_VHOST",
)


def clear_broker_env(monkeypatch):
    for env_var in BROKER_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)


@pytest.mark.unit
class TestCeleryBrokerUrl:
    def test_celery_broker_url_wins_over_amqp_url(self, monkeypatch):
        clear_broker_env(monkeypatch)
        monkeypatch.setenv("CELERY_BROKER_URL", "redis://render-key-value:6379/0")
        monkeypatch.setenv("AMQP_URL", "amqps://cloudamqp.example/vhost")

        assert _resolve_celery_broker_url() == "redis://render-key-value:6379/0"

    def test_amqp_url_is_used_when_celery_broker_url_is_absent(self, monkeypatch):
        clear_broker_env(monkeypatch)
        monkeypatch.setenv("AMQP_URL", "amqps://cloudamqp.example/vhost")

        assert _resolve_celery_broker_url() == "amqps://cloudamqp.example/vhost"

    def test_empty_celery_broker_url_does_not_shadow_amqp_url(self, monkeypatch):
        clear_broker_env(monkeypatch)
        monkeypatch.setenv("CELERY_BROKER_URL", "")
        monkeypatch.setenv("AMQP_URL", "amqps://cloudamqp.example/vhost")

        assert _resolve_celery_broker_url() == "amqps://cloudamqp.example/vhost"

    def test_local_rabbitmq_fallback_uses_configured_fields(self, monkeypatch):
        clear_broker_env(monkeypatch)
        monkeypatch.setenv("RABBITMQ_HOST", "rabbitmq.local")
        monkeypatch.setenv("RABBITMQ_PORT", "5673")
        monkeypatch.setenv("RABBITMQ_USER", "worker")
        monkeypatch.setenv("RABBITMQ_PASSWORD", "worker-pass")
        monkeypatch.setenv("RABBITMQ_VHOST", "bright-byte")

        assert _resolve_celery_broker_url() == "amqp://worker:worker-pass@rabbitmq.local:5673/bright-byte"
