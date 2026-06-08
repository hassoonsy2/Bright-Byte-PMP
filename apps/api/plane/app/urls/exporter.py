# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.app.views import ExportIssuesEndpoint, WorkItemImportEndpoint


urlpatterns = [
    path(
        "workspaces/<str:slug>/export-issues/",
        ExportIssuesEndpoint.as_view(),
        name="export-issues",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/import-work-items/",
        WorkItemImportEndpoint.as_view(),
        name="import-work-items",
    ),
]
