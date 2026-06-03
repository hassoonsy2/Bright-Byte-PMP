# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Test Settings"""

import os

# Ensure the boot-time security guard in common.py does not fire during the
# test run.  The guard is intentionally gated on `not DEBUG` — setting
# DEBUG=1 in the environment before importing common means the guard is
# silent, which is the correct behaviour for local/CI test execution.
os.environ.setdefault("DEBUG", "1")
# Provide a stable dummy SECRET_KEY so the guard's SECRET_KEY check is also
# satisfied when the test suite is run in a minimal environment.
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-not-for-production")

from .common import *  # noqa

DEBUG = True

# Send it in a dummy outbox
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

INSTALLED_APPS.append(  # noqa
    "plane.tests"
)
