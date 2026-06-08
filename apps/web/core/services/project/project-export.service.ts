/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@bright-byte/constants";
import type { TWorkItemFilterExpression } from "@bright-byte/types";
import { APIService } from "@/services/api.service";
// helpers

export class ProjectExportService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async csvExport(
    workspaceSlug: string,
    data: {
      provider: string;
      project: string[];
      multiple?: boolean;
      rich_filters?: TWorkItemFilterExpression;
    }
  ): Promise<any> {
    return this.post(`/api/workspaces/${workspaceSlug}/export-issues/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async importWorkItems(
    workspaceSlug: string,
    projectId: string,
    file: File
  ): Promise<{
    created: number;
    failed: number;
    total: number;
    errors: { row: number; name: string; error: string }[];
  }> {
    const formData = new FormData();
    formData.append("file", file);
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/import-work-items/`, formData)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
