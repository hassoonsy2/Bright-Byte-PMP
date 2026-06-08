/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { EUserPermissions, EUserPermissionsLevel } from "@bright-byte/constants";
import { useTranslation } from "@bright-byte/i18n";
import { cn } from "@bright-byte/utils";
// components
import { NotAuthorizedView } from "@/components/auth-screens/not-authorized-view";
import { PageHead } from "@/components/core/page-title";
import { ExportGuide } from "@/components/exporter/guide";
import { ImportForm } from "@/components/exporter/import-form";
import { SettingsContentWrapper } from "@/components/settings/content-wrapper";
import { SettingsHeading } from "@/components/settings/heading";
// hooks
import { useWorkspace } from "@/hooks/store/use-workspace";
import { useUserPermissions } from "@/hooks/store/user";
// local imports
import { ExportsWorkspaceSettingsHeader } from "./header";

function ExportsPage() {
  // router
  const { workspaceSlug } = useParams();
  // store hooks
  const { workspaceUserInfo, allowPermissions } = useUserPermissions();
  const { currentWorkspace } = useWorkspace();
  const { t } = useTranslation();

  // derived values
  const canPerformWorkspaceMemberActions = allowPermissions(
    [EUserPermissions.ADMIN, EUserPermissions.MEMBER],
    EUserPermissionsLevel.WORKSPACE
  );
  const pageTitle = currentWorkspace?.name
    ? `${currentWorkspace.name} - ${t("workspace_settings.settings.exports.title")}`
    : undefined;

  // if user is not authorized to view this page
  if (workspaceUserInfo && !canPerformWorkspaceMemberActions) {
    return <NotAuthorizedView section="settings" className="h-auto" />;
  }

  return (
    <SettingsContentWrapper header={<ExportsWorkspaceSettingsHeader />} hugging>
      <PageHead title={pageTitle} />
      <div
        className={cn("flex w-full flex-col gap-y-10", {
          "opacity-60": !canPerformWorkspaceMemberActions,
        })}
      >
        <div className="flex flex-col gap-y-6">
          <SettingsHeading
            title={t("workspace_settings.settings.imports.heading", { defaultValue: "Import work items" })}
            description={t("workspace_settings.settings.imports.description", {
              defaultValue: "Bulk-create work items in a project from a CSV or Excel file.",
            })}
          />
          <ImportForm workspaceSlug={workspaceSlug?.toString()} />
        </div>
        <div className="flex flex-col gap-y-6">
          <SettingsHeading
            title={t("workspace_settings.settings.exports.heading")}
            description={t("workspace_settings.settings.exports.description")}
          />
          <ExportGuide />
        </div>
      </div>
    </SettingsContentWrapper>
  );
}

export default observer(ExportsPage);
