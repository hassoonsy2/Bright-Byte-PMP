/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useRef, useState } from "react";
import { intersection } from "lodash-es";
import { observer } from "mobx-react";
import { Download, Upload } from "lucide-react";
// plane imports
import { EUserPermissions, EUserPermissionsLevel } from "@bright-byte/constants";
import { useTranslation } from "@bright-byte/i18n";
import { Button } from "@bright-byte/propel/button";
import { TOAST_TYPE, setToast } from "@bright-byte/propel/toast";
import { CustomSearchSelect } from "@bright-byte/ui";
// hooks
import { useProject } from "@/hooks/store/use-project";
import { useUser, useUserPermissions } from "@/hooks/store/user";
// services
import { ProjectExportService } from "@/services/project/project-export.service";
// local imports
import { SettingsBoxedControlItem } from "../settings/boxed-control-item";

const projectExportService = new ProjectExportService();

const escapeCsvCell = (value: string) => `"${value.replace(/"/g, '""')}"`;

// Template column layout — matches the work-item export so an export can be re-imported.
const TEMPLATE_HEADERS = [
  "Name",
  "Description",
  "State Name",
  "Priority",
  "Start Date",
  "Target Date",
  "Duration",
  "Estimate Time",
  "Labels",
];
const TEMPLATE_EXAMPLE = [
  "Design the landing page",
  "Hero section and pricing table",
  "Todo",
  "high",
  "2026-06-01",
  "2026-06-10",
  "2h 30m",
  "4h",
  "frontend,design",
];

type Props = {
  workspaceSlug: string;
};

export const ImportForm = observer(function ImportForm(props: Props) {
  const { workspaceSlug } = props;
  // i18n
  const { t } = useTranslation();
  // store hooks
  const { allowPermissions } = useUserPermissions();
  const { canPerformAnyCreateAction, projectsWithCreatePermissions } = useUser();
  const { workspaceProjectIds, getProjectById } = useProject();
  // refs + state
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  // derived values
  const hasProjects = workspaceProjectIds && workspaceProjectIds.length > 0;
  const isMember = allowPermissions([EUserPermissions.ADMIN, EUserPermissions.MEMBER], EUserPermissionsLevel.WORKSPACE);
  const wsProjectIds = projectsWithCreatePermissions
    ? intersection(workspaceProjectIds, Object.keys(projectsWithCreatePermissions))
    : [];
  const options = wsProjectIds?.map((id) => {
    const projectDetails = getProjectById(id);
    return {
      value: projectDetails?.id,
      query: `${projectDetails?.name} ${projectDetails?.identifier}`,
      content: (
        <div className="flex items-center gap-2">
          <span className="flex-shrink-0 text-10 text-secondary">{projectDetails?.identifier}</span>
          <span className="truncate">{projectDetails?.name}</span>
        </div>
      ),
    };
  });
  const selectedProject = projectId ? getProjectById(projectId) : undefined;
  const disabled = !isMember && (!hasProjects || !canPerformAnyCreateAction);

  const handleDownloadTemplate = () => {
    const csv = [TEMPLATE_HEADERS.map(escapeCsvCell).join(","), TEMPLATE_EXAMPLE.map(escapeCsvCell).join(",")].join(
      "\n"
    );
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "work-items-import-template.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = async () => {
    if (!projectId || !file || loading) return;
    setLoading(true);
    try {
      const result = await projectExportService.importWorkItems(workspaceSlug, projectId, file);
      setToast({
        type: result.created > 0 ? TOAST_TYPE.SUCCESS : TOAST_TYPE.ERROR,
        title: result.created > 0 ? "Import complete" : "Nothing imported",
        message:
          `Created ${result.created} work item${result.created === 1 ? "" : "s"}` +
          (result.failed ? `, ${result.failed} row${result.failed === 1 ? "" : "s"} failed.` : "."),
      });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (error) {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: "Import failed",
        message: (error as { error?: string })?.error ?? "Could not import the file. Check the format and try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="rounded-lg border border-subtle bg-layer-2">
        {/* Project selector */}
        <SettingsBoxedControlItem
          className="rounded-none border-0 border-b"
          title={t("common.project", { defaultValue: "Project" })}
          control={
            <CustomSearchSelect
              value={projectId ?? ""}
              onChange={(val: string) => setProjectId(val)}
              options={options}
              input
              disabled={disabled}
              label={selectedProject ? `${selectedProject.identifier} ${selectedProject.name}` : "Select a project"}
              optionsClassName="max-w-48 sm:max-w-[532px]"
              placement="bottom-end"
            />
          }
        />
        {/* File picker */}
        <SettingsBoxedControlItem
          className="rounded-none border-0 border-b"
          title={t("common.file", { defaultValue: "File (.csv or .xlsx)" })}
          control={
            <div className="flex items-center justify-end gap-2">
              <span className="max-w-48 truncate text-13 text-secondary">{file?.name ?? "No file selected"}</span>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
              <Button variant="secondary" size="sm" disabled={disabled} onClick={() => fileInputRef.current?.click()}>
                {file ? "Change file" : "Choose file"}
              </Button>
            </div>
          }
        />
        <div className="flex items-center justify-between gap-3 px-4 py-3">
          <Button
            variant="link"
            size="sm"
            prependIcon={<Download className="h-3.5 w-3.5" />}
            onClick={handleDownloadTemplate}
          >
            Download template
          </Button>
          <Button
            variant="primary"
            size="lg"
            prependIcon={<Upload className="h-3.5 w-3.5" />}
            loading={loading}
            disabled={!projectId || !file || disabled}
            onClick={() => {
              void handleImport();
            }}
          >
            {loading ? "Importing..." : "Import work items"}
          </Button>
        </div>
      </div>
      <p className="text-13 text-tertiary">
        Upload a CSV or Excel file. Recognised columns: Name (required), Description, State Name, Priority, Start Date,
        Target Date, Duration, Estimate Time, Labels. A work-item export can be re-imported as-is.
      </p>
    </div>
  );
});
