/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@bright-byte/constants";
import { APIService } from "@/services/api.service";

export const PROJECT_SLACK_NOTIFICATION_TOGGLE_KEYS = [
  "notify_issue_created",
  "notify_state_changed",
  "notify_assignee_changed",
  "notify_priority_changed",
  "notify_comment_created",
  "notify_issue_deleted",
] as const;

export type TProjectSlackNotificationToggleKey = (typeof PROJECT_SLACK_NOTIFICATION_TOGGLE_KEYS)[number];

export type TProjectSlackNotification = {
  id: string | null;
  project_id: string;
  has_webhook_url: boolean;
  webhook_url_masked: string;
  is_active: boolean;
  last_delivered_at: string | null;
  last_error: string;
} & Record<TProjectSlackNotificationToggleKey, boolean>;

export type TProjectSlackNotificationUpdatePayload = Partial<
  Pick<TProjectSlackNotification, "is_active" | TProjectSlackNotificationToggleKey>
> & { webhook_url?: string };

export type TProjectSlackNotificationTestResult = { success: boolean; error?: string };

export class ProjectSlackNotificationService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  private baseUrl(workspaceSlug: string, projectId: string) {
    return `/api/workspaces/${workspaceSlug}/projects/${projectId}/slack-notification/`;
  }

  /** Resolves null when the workspace does not have Slack notifications (the API answers 404). */
  async retrieve(workspaceSlug: string, projectId: string): Promise<TProjectSlackNotification | null> {
    return this.get(this.baseUrl(workspaceSlug, projectId))
      .then((response) => response?.data)
      .catch((error) => {
        if (error?.response?.status === 404) return null;
        throw error?.response?.data;
      });
  }

  async update(
    workspaceSlug: string,
    projectId: string,
    data: TProjectSlackNotificationUpdatePayload
  ): Promise<TProjectSlackNotification> {
    return this.patch(this.baseUrl(workspaceSlug, projectId), data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async remove(workspaceSlug: string, projectId: string): Promise<void> {
    return this.delete(this.baseUrl(workspaceSlug, projectId))
      .then(() => undefined)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async sendTest(workspaceSlug: string, projectId: string): Promise<TProjectSlackNotificationTestResult> {
    return this.post(`${this.baseUrl(workspaceSlug, projectId)}test/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
