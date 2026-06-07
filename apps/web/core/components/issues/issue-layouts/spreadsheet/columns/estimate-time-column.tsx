/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
// types
import type { TIssue } from "@bright-byte/types";
import { formatSecondsToDuration, parseDurationToSeconds } from "@bright-byte/utils";

type Props = {
  issue: TIssue;
  onClose: () => void;
  onChange: (issue: TIssue, data: Partial<TIssue>, updates: any) => void;
  disabled: boolean;
};

export const SpreadsheetEstimateTimeColumn = observer(function SpreadsheetEstimateTimeColumn(props: Props) {
  const { issue, onChange, disabled } = props;

  return (
    <div className="flex h-11 w-full items-center border-b-[0.5px] border-subtle">
      <input
        key={`estimate-time-${issue.estimate_time ?? ""}`}
        type="text"
        defaultValue={formatSecondsToDuration(issue.estimate_time)}
        placeholder="—"
        disabled={disabled}
        className="h-full w-full border-none bg-transparent px-page-x text-13 text-secondary outline-none group-[.selected-issue-row]:bg-accent-primary/5 placeholder:text-placeholder hover:bg-layer-1 group-[.selected-issue-row]:hover:bg-accent-primary/10 focus:bg-layer-1 disabled:cursor-not-allowed"
        onKeyDown={(e) => {
          if (e.key === "Enter") e.currentTarget.blur();
        }}
        onBlur={(e) => {
          const nextValue = parseDurationToSeconds(e.target.value);
          if (nextValue !== (issue.estimate_time ?? null)) {
            onChange(
              issue,
              { estimate_time: nextValue },
              { changed_property: "estimate_time", change_details: nextValue }
            );
          }
        }}
      />
    </div>
  );
});
