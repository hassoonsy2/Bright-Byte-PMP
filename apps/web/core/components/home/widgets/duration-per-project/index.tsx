/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useRef } from "react";
import { observer } from "mobx-react";
import { Timer } from "lucide-react";
import useSWR from "swr";
// plane imports
import { useTranslation } from "@bright-byte/i18n";
import type { THomeWidgetProps } from "@bright-byte/types";
import { formatSecondsToDuration } from "@bright-byte/utils";
// components
import { ContentOverflowWrapper } from "@/components/core/content-overflow-HOC";
// services
import { WorkspaceService } from "@/services/workspace.service";

const workspaceService = new WorkspaceService();
const SKELETON_ROWS = ["s1", "s2", "s3", "s4"];

export const DurationPerProjectWidget = observer(function DurationPerProjectWidget(props: THomeWidgetProps) {
  const { workspaceSlug } = props;
  // i18n
  const { t } = useTranslation();
  // ref
  const ref = useRef<HTMLDivElement>(null);

  const { data, isLoading } = useSWR(
    workspaceSlug ? `WORKSPACE_DURATION_PER_PROJECT_${workspaceSlug}` : null,
    workspaceSlug ? () => workspaceService.fetchWorkspaceDurationPerProject(workspaceSlug.toString()) : null,
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  const title = t("home.duration_per_project.title", { defaultValue: "Duration per project" });
  const projects = data ?? [];
  const maxDuration = projects.reduce((max, project) => Math.max(max, project.total_duration), 0);

  if (!isLoading && projects.length === 0)
    return (
      <div ref={ref}>
        <div className="mb-4 flex items-center gap-2">
          <Timer className="h-4 w-4 text-tertiary" />
          <div className="text-14 font-semibold text-tertiary">{title}</div>
        </div>
        <div className="flex min-h-[120px] flex-col items-center justify-center rounded-lg border border-subtle px-4 text-center text-13 text-tertiary">
          {t("home.duration_per_project.empty", {
            defaultValue: "Track time on work items to see total duration per project here.",
          })}
        </div>
      </div>
    );

  return (
    <ContentOverflowWrapper
      maxHeight={415}
      containerClassName="box-border min-h-[120px]"
      fallback={<></>}
      buttonClassName="bg-surface-2/20"
    >
      <div className="mb-3 flex items-center gap-2">
        <Timer className="h-4 w-4 text-tertiary" />
        <div className="text-14 font-semibold text-tertiary">{title}</div>
      </div>
      <div className="flex flex-col gap-2.5">
        {isLoading
          ? SKELETON_ROWS.map((id) => <div key={id} className="h-8 w-full animate-pulse rounded-md bg-layer-1" />)
          : projects.map((project) => {
              const widthPct = maxDuration > 0 ? Math.max((project.total_duration / maxDuration) * 100, 4) : 0;
              return (
                <div key={project.project_id} className="flex items-center gap-3">
                  <div className="flex w-32 flex-shrink-0 items-center gap-1.5 truncate text-13 text-secondary">
                    <span className="flex-shrink-0 text-10 text-tertiary">{project.project_identifier}</span>
                    <span className="truncate">{project.project_name}</span>
                  </div>
                  <div className="relative h-6 flex-1 overflow-hidden rounded-md bg-layer-1">
                    <div
                      className="absolute top-0 left-0 h-full rounded-md bg-accent-primary/70"
                      style={{ width: `${widthPct}%` }}
                    />
                  </div>
                  <div className="w-20 flex-shrink-0 text-right text-13 font-medium text-secondary">
                    {formatSecondsToDuration(project.total_duration)}
                  </div>
                </div>
              );
            })}
      </div>
    </ContentOverflowWrapper>
  );
});
