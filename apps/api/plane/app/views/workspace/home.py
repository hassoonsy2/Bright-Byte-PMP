# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Module imports
from ..base import BaseAPIView
from plane.db.models.workspace import WorkspaceHomePreference
from plane.app.permissions import allow_permission, ROLE
from plane.db.models import Workspace, Issue, Project
from plane.app.serializers.workspace import WorkspaceHomePreferenceSerializer

# Third party imports
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status


class WorkspaceHomePreferenceViewSet(BaseAPIView):
    model = WorkspaceHomePreference

    def get_serializer_class(self):
        return WorkspaceHomePreferenceSerializer

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST], level="WORKSPACE")
    def get(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)

        get_preference = WorkspaceHomePreference.objects.filter(user=request.user, workspace_id=workspace.id)

        create_preference_keys = []

        keys = [
            key
            for key, _ in WorkspaceHomePreference.HomeWidgetKeys.choices
            if key not in ["quick_tutorial", "new_at_plane"]
        ]

        sort_order_counter = 1

        for preference in keys:
            if preference not in get_preference.values_list("key", flat=True):
                create_preference_keys.append(preference)

                sort_order = 1000 - sort_order_counter

                preference = WorkspaceHomePreference.objects.bulk_create(
                    [
                        WorkspaceHomePreference(
                            key=key,
                            user=request.user,
                            workspace=workspace,
                            sort_order=sort_order,
                        )
                        for key in create_preference_keys
                    ],
                    batch_size=10,
                    ignore_conflicts=True,
                )
                sort_order_counter += 1

        preference = WorkspaceHomePreference.objects.filter(user=request.user, workspace_id=workspace.id)

        return Response(
            preference.values("key", "is_enabled", "config", "sort_order"),
            status=status.HTTP_200_OK,
        )

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST], level="WORKSPACE")
    def patch(self, request, slug, key):
        preference = WorkspaceHomePreference.objects.filter(key=key, workspace__slug=slug, user=request.user).first()

        if preference:
            serializer = WorkspaceHomePreferenceSerializer(preference, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Preference not found"}, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceDurationPerProjectEndpoint(BaseAPIView):
    """Aggregate the total work-item duration (in seconds) per project for the home widget."""

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST], level="WORKSPACE")
    def get(self, request, slug):
        # Restrict to projects the requesting user is an active member of
        project_ids = Project.objects.filter(
            workspace__slug=slug,
            project_projectmember__member=request.user,
            project_projectmember__is_active=True,
            archived_at__isnull=True,
        ).values_list("id", flat=True)

        project_aggregations = (
            Issue.issue_objects.filter(workspace__slug=slug, project_id__in=project_ids)
            .values("project_id", "project__name", "project__identifier")
            .annotate(total_duration=Sum("duration"))
            .filter(total_duration__gt=0)
            .order_by("-total_duration")
        )

        data = [
            {
                "project_id": str(item["project_id"]),
                "project_name": item["project__name"],
                "project_identifier": item["project__identifier"],
                "total_duration": item["total_duration"],
            }
            for item in project_aggregations
        ]

        return Response(data, status=status.HTTP_200_OK)
