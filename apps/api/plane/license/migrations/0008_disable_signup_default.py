# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Force the instance to invite-only. configure_instance seeds configs
# create-only, so an instance first booted before ENABLE_SIGNUP=0 was set keeps
# the old "1" value. This one-time data migration flips the existing row (or
# creates it) to "0". An admin can still re-enable signup later via god-mode;
# this migration runs once and will not override a later change.

from django.db import migrations


def disable_signup(apps, schema_editor):
    InstanceConfiguration = apps.get_model("license", "InstanceConfiguration")
    InstanceConfiguration.objects.update_or_create(
        key="ENABLE_SIGNUP",
        defaults={"value": "0", "category": "AUTHENTICATION", "is_encrypted": False},
    )


def noop_reverse(apps, schema_editor):
    # Do not auto re-enable signup on reverse.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("license", "0007_disable_telemetry_default"),
    ]

    operations = [
        migrations.RunPython(disable_signup, noop_reverse),
    ]
