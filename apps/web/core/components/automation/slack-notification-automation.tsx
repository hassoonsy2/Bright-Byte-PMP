/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { observer } from "mobx-react";
import { BellRing } from "lucide-react";
// plane imports
import { EUserPermissions, EUserPermissionsLevel } from "@bright-byte/constants";
import { useTranslation } from "@bright-byte/i18n";
import { Button } from "@bright-byte/propel/button";
import { TOAST_TYPE, setToast } from "@bright-byte/propel/toast";
import { Input, ToggleSwitch } from "@bright-byte/ui";
// components
import { SettingsControlItem } from "@/components/settings/control-item";
// hooks
import { useProjectSlackNotification } from "@/hooks/use-project-slack-notification";
import { useUserPermissions } from "@/hooks/store/user";
// services
import { PROJECT_SLACK_NOTIFICATION_TOGGLE_KEYS } from "@/services/project/project-slack-notification.service";
import type {
  TProjectSlackNotification,
  TProjectSlackNotificationToggleKey,
  TProjectSlackNotificationUpdatePayload,
} from "@/services/project/project-slack-notification.service";

type Props = {
  workspaceSlug: string;
  projectId: string;
};

type TToggles = Record<TProjectSlackNotificationToggleKey, boolean>;

const SLACK_WEBHOOK_PREFIX = "https://hooks.slack.com/services/";

const TOGGLE_LABELS: Record<TProjectSlackNotificationToggleKey, string> = {
  notify_issue_created: "Work item created",
  notify_state_changed: "State changed",
  notify_assignee_changed: "Assignee changed",
  notify_priority_changed: "Priority changed",
  notify_comment_created: "Comment added",
  notify_issue_deleted: "Work item deleted",
};

const getToggles = (config: TProjectSlackNotification): TToggles => {
  const toggles = {} as TToggles;
  for (const key of PROJECT_SLACK_NOTIFICATION_TOGGLE_KEYS) toggles[key] = config[key];
  return toggles;
};

const getErrorMessage = (error: unknown, fallback: string) =>
  (error as { error?: string } | undefined)?.error ?? fallback;

export const SlackNotificationAutomation = observer(function SlackNotificationAutomation(props: Props) {
  const { workspaceSlug, projectId } = props;
  // states
  const [webhookUrl, setWebhookUrl] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [toggles, setToggles] = useState<TToggles | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  // store hooks
  const { allowPermissions } = useUserPermissions();
  const { t } = useTranslation();
  const { config, error, updateConfig, removeConfig, sendTestMessage } = useProjectSlackNotification(
    workspaceSlug,
    projectId
  );

  useEffect(() => {
    if (!config) return;
    setIsActive(config.is_active);
    setToggles(getToggles(config));
  }, [config]);

  // Nothing renders while loading, on errors, or when the workspace doesn't have the feature (API 404 -> null)
  if (error || !config || !toggles) return null;

  const isAdmin = allowPermissions([EUserPermissions.ADMIN], EUserPermissionsLevel.PROJECT, workspaceSlug, projectId);
  const trimmedUrl = webhookUrl.trim();
  const isUrlInvalid = trimmedUrl !== "" && !trimmedUrl.startsWith(SLACK_WEBHOOK_PREFIX);
  const isDirty =
    trimmedUrl !== "" ||
    isActive !== config.is_active ||
    PROJECT_SLACK_NOTIFICATION_TOGGLE_KEYS.some((key) => toggles[key] !== config[key]);
  const canSave = isAdmin && isDirty && !isUrlInvalid && (config.has_webhook_url || trimmedUrl !== "");

  const handleSave = async () => {
    const payload: TProjectSlackNotificationUpdatePayload = { is_active: isActive, ...toggles };
    if (trimmedUrl) payload.webhook_url = trimmedUrl;

    setIsSaving(true);
    try {
      await updateConfig(payload);
      setWebhookUrl("");
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("project_settings.automations.slack.saved", { defaultValue: "Slack notifications saved" }),
      });
    } catch (err) {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("common.error.label", { defaultValue: "Error!" }),
        message: getErrorMessage(err, "Could not save Slack notifications. Please try again."),
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleSendTest = async () => {
    setIsTesting(true);
    try {
      await sendTestMessage();
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("project_settings.automations.slack.test_sent", { defaultValue: "Test message sent" }),
      });
    } catch (err) {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("project_settings.automations.slack.test_failed", { defaultValue: "Test message failed" }),
        message: getErrorMessage(err, "Slack did not accept the message."),
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleDisconnect = async () => {
    setIsRemoving(true);
    try {
      await removeConfig();
      setWebhookUrl("");
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("project_settings.automations.slack.disconnected", { defaultValue: "Slack disconnected" }),
      });
    } catch (err) {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("common.error.label", { defaultValue: "Error!" }),
        message: getErrorMessage(err, "Could not disconnect Slack. Please try again."),
      });
    } finally {
      setIsRemoving(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 border-b border-subtle py-2">
      <div className="flex items-center gap-3">
        <div className="grid size-10 shrink-0 place-items-center rounded-sm bg-layer-2">
          <BellRing className="size-4 shrink-0 text-primary" />
        </div>
        <SettingsControlItem
          title={t("project_settings.automations.slack.title", { defaultValue: "Slack notifications" })}
          description={t("project_settings.automations.slack.description", {
            defaultValue: "Send this project's work item updates to a Slack channel.",
          })}
          control={<ToggleSwitch value={isActive} onChange={setIsActive} size="sm" disabled={!isAdmin} />}
        />
      </div>
      <div className="ml-13">
        <div className="flex w-full flex-col gap-4 rounded-sm border border-subtle bg-surface-2 px-5 py-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="slack-webhook-url" className="text-13 font-medium">
              {t("project_settings.automations.slack.webhook_url", { defaultValue: "Slack webhook URL" })}
            </label>
            <Input
              id="slack-webhook-url"
              type="url"
              autoComplete="off"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              placeholder={config.has_webhook_url ? config.webhook_url_masked : `${SLACK_WEBHOOK_PREFIX}…`}
              hasError={isUrlInvalid}
              disabled={!isAdmin}
              className="w-full"
            />
            {isUrlInvalid ? (
              <span className="text-13 text-danger-primary">
                {t("project_settings.automations.slack.invalid_url", {
                  defaultValue: "Use a Slack incoming webhook URL that starts with https://hooks.slack.com/services/",
                })}
              </span>
            ) : (
              config.has_webhook_url && (
                <span className="text-13 text-tertiary">
                  {t("project_settings.automations.slack.replace_url", {
                    defaultValue: "A webhook is saved. Paste a new URL only to replace it.",
                  })}
                </span>
              )
            )}
          </div>
          <div className="flex flex-col">
            {PROJECT_SLACK_NOTIFICATION_TOGGLE_KEYS.map((key) => (
              <SettingsControlItem
                key={key}
                title={t(`project_settings.automations.slack.${key}`, { defaultValue: TOGGLE_LABELS[key] })}
                description=""
                control={
                  <ToggleSwitch
                    value={toggles[key]}
                    onChange={(value) => setToggles({ ...toggles, [key]: value })}
                    size="sm"
                    disabled={!isAdmin}
                  />
                }
              />
            ))}
          </div>
          {config.last_error ? (
            <p className="text-13 text-danger-primary">
              {t("project_settings.automations.slack.last_error", { defaultValue: "Last delivery failed:" })}{" "}
              {config.last_error}
            </p>
          ) : (
            config.last_delivered_at && (
              <p className="text-13 text-tertiary">
                {t("project_settings.automations.slack.last_delivered", { defaultValue: "Last delivered:" })}{" "}
                {new Date(config.last_delivered_at).toLocaleString()}
              </p>
            )
          )}
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="primary"
              size="sm"
              loading={isSaving}
              disabled={!canSave}
              onClick={() => {
                void handleSave();
              }}
            >
              {t("common.save", { defaultValue: "Save" })}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              loading={isTesting}
              disabled={!isAdmin || !config.has_webhook_url || isDirty}
              title={
                isDirty
                  ? t("project_settings.automations.slack.save_first", { defaultValue: "Save your changes first" })
                  : undefined
              }
              onClick={() => {
                void handleSendTest();
              }}
            >
              {t("project_settings.automations.slack.send_test", { defaultValue: "Send test message" })}
            </Button>
            {config.id && (
              <Button
                variant="error-outline"
                size="sm"
                loading={isRemoving}
                disabled={!isAdmin}
                onClick={() => {
                  void handleDisconnect();
                }}
              >
                {t("project_settings.automations.slack.disconnect", { defaultValue: "Disconnect" })}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});
