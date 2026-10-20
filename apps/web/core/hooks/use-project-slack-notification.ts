/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import useSWR from "swr";
// services
import { ProjectSlackNotificationService } from "@/services/project/project-slack-notification.service";
import type { TProjectSlackNotificationUpdatePayload } from "@/services/project/project-slack-notification.service";

const projectSlackNotificationService = new ProjectSlackNotificationService();

export function useProjectSlackNotification(workspaceSlug: string, projectId: string) {
  const { data, error, isLoading, mutate } = useSWR(
    workspaceSlug && projectId ? `PROJECT_SLACK_NOTIFICATION_${workspaceSlug}_${projectId}` : null,
    () => projectSlackNotificationService.retrieve(workspaceSlug, projectId),
    { revalidateOnFocus: false, shouldRetryOnError: false }
  );

  const updateConfig = async (payload: TProjectSlackNotificationUpdatePayload) => {
    const result = await projectSlackNotificationService.update(workspaceSlug, projectId, payload);
    await mutate(result, { revalidate: false });
    return result;
  };

  const removeConfig = async () => {
    await projectSlackNotificationService.remove(workspaceSlug, projectId);
    await mutate();
  };

  const sendTestMessage = async () => {
    try {
      return await projectSlackNotificationService.sendTest(workspaceSlug, projectId);
    } finally {
      // refresh last_delivered_at / last_error either way
      await mutate();
    }
  };

  return { config: data, error, isLoading, updateConfig, removeConfig, sendTestMessage };
}
