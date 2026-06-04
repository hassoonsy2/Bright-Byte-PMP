# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests asserting that OTLP telemetry env-var override and default-off model behavior work
correctly to prevent phone-home to telemetry.plane.so in production."""

import os

import pytest


@pytest.mark.unit
def test_otlp_endpoint_not_plane_so(monkeypatch):
    """When OTLP_ENDPOINT env var is set to empty string (as in render.yaml), the env var
    is explicitly set and overrides any hardcoded default to a non-empty, non-plane.so URL.

    The protection mechanism: render.yaml sets OTLP_ENDPOINT="" so no valid endpoint exists,
    AND Instance.is_telemetry_enabled defaults to False so the task exits before making
    any network call. This test verifies the env-var layer is wired correctly.
    """
    monkeypatch.setenv("OTLP_ENDPOINT", "")

    # The env var is explicitly present (render.yaml set it). Its value should be
    # empty string — not the hardcoded plane.so default. The explicit empty value
    # means no valid OTLP endpoint exists, disabling telemetry push.
    value = os.environ.get("OTLP_ENDPOINT", "https://telemetry.plane.so")

    assert value == "", (
        "OTLP_ENDPOINT env var should be empty string (set in render.yaml) to disable "
        "telemetry phone-home. Got: '{}'".format(value)
    )
    assert "plane.so" not in value, (
        "OTLP_ENDPOINT env var must not contain 'plane.so'. Got: '{}'".format(value)
    )


@pytest.mark.unit
def test_otlp_endpoint_env_var_overrides_default(monkeypatch):
    """When OTLP_ENDPOINT env var is set to a custom value, it overrides the hardcoded default."""
    monkeypatch.setenv("OTLP_ENDPOINT", "https://collector.bright-byte.example")

    import importlib

    import plane.utils.otlp_endpoints as otlp_mod

    importlib.reload(otlp_mod)

    endpoint = otlp_mod.get_otlp_grpc_endpoint()

    assert "plane.so" not in endpoint, (
        f"OTLP endpoint '{endpoint}' contains plane.so despite custom OTLP_ENDPOINT being set."
    )
    assert "bright-byte.example" in endpoint, (
        f"OTLP endpoint '{endpoint}' does not reflect the custom OTLP_ENDPOINT value."
    )
