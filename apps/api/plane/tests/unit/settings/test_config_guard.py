# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for the boot-time security guard in plane.settings.common."""

import pytest

from plane.settings.common import check_boot_security


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Default "safe" values used as a baseline in each test so tests only vary
# the dimension they are testing.
_SAFE_ENVIRON = {"SECRET_KEY": "stable-secret-key-for-tests"}
_DEBUG_OFF = False
_DEBUG_ON = True
_SAFE_HOSTS = ["bright-byte-api.onrender.com"]
_WILDCARD_HOSTS = ["*"]
_CORS_ALLOW_ALL_OFF = False
_CORS_ALLOW_ALL_ON = True
_CORS_CREDENTIALS_ON = True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_boot_guard_requires_secret_key():
    """Guard returns an error when SECRET_KEY env var is absent."""
    errors = check_boot_security(
        environ={},  # no SECRET_KEY
        debug=_DEBUG_OFF,
        allowed_hosts=_SAFE_HOSTS,
        cors_allow_all_origins=_CORS_ALLOW_ALL_OFF,
        cors_allow_credentials=_CORS_CREDENTIALS_ON,
    )
    assert any("SECRET_KEY" in e for e in errors), f"Expected SECRET_KEY error, got: {errors}"


@pytest.mark.unit
def test_boot_guard_rejects_allow_all_cors():
    """Guard returns an error when CORS_ALLOW_ALL_ORIGINS=True with credentials active."""
    errors = check_boot_security(
        environ=_SAFE_ENVIRON,
        debug=_DEBUG_OFF,
        allowed_hosts=_SAFE_HOSTS,
        cors_allow_all_origins=_CORS_ALLOW_ALL_ON,
        cors_allow_credentials=_CORS_CREDENTIALS_ON,
    )
    assert any("CORS_ALLOW_ALL_ORIGINS" in e for e in errors), (
        f"Expected CORS_ALLOW_ALL_ORIGINS error, got: {errors}"
    )


@pytest.mark.unit
def test_boot_guard_rejects_wildcard_allowed_hosts():
    """Guard returns an error when ALLOWED_HOSTS contains '*' in non-DEBUG mode."""
    errors = check_boot_security(
        environ=_SAFE_ENVIRON,
        debug=_DEBUG_OFF,
        allowed_hosts=_WILDCARD_HOSTS,
        cors_allow_all_origins=_CORS_ALLOW_ALL_OFF,
        cors_allow_credentials=_CORS_CREDENTIALS_ON,
    )
    assert any("ALLOWED_HOSTS" in e for e in errors), (
        f"Expected ALLOWED_HOSTS error, got: {errors}"
    )


@pytest.mark.unit
def test_boot_guard_silent_in_debug():
    """Guard returns no ALLOWED_HOSTS error when DEBUG=True, even with worst-case env."""
    # Supply the absolute worst-case configuration: no SECRET_KEY, wildcard hosts,
    # and CORS allow-all+credentials.  The guard must still not raise in DEBUG mode —
    # it will return errors for SECRET_KEY and CORS (those checks are not debug-gated),
    # but the ALLOWED_HOSTS wildcard check is gated on `not debug`.
    errors_wildcard = check_boot_security(
        environ={},  # no SECRET_KEY
        debug=_DEBUG_ON,
        allowed_hosts=_WILDCARD_HOSTS,
        cors_allow_all_origins=_CORS_ALLOW_ALL_ON,
        cors_allow_credentials=_CORS_CREDENTIALS_ON,
    )
    # The ALLOWED_HOSTS wildcard must NOT generate an error when debug=True.
    assert not any("ALLOWED_HOSTS" in e for e in errors_wildcard), (
        "Guard must not flag ALLOWED_HOSTS wildcard when DEBUG=True — "
        f"but got: {errors_wildcard}"
    )

    # Confirm that a fully safe config in debug mode returns zero errors.
    errors_safe = check_boot_security(
        environ=_SAFE_ENVIRON,
        debug=_DEBUG_ON,
        allowed_hosts=_SAFE_HOSTS,
        cors_allow_all_origins=_CORS_ALLOW_ALL_OFF,
        cors_allow_credentials=_CORS_CREDENTIALS_ON,
    )
    assert errors_safe == [], f"Expected no errors for safe debug config, got: {errors_safe}"
