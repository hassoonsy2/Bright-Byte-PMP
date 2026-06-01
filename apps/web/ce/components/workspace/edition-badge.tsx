/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
// ui
import { Badge } from "@bright-byte/propel/badge";
import { Tooltip } from "@bright-byte/propel/tooltip";
// hooks
import { usePlatformOS } from "@/hooks/use-platform-os";
import packageJson from "package.json";

export const WorkspaceEditionBadge = observer(function WorkspaceEditionBadge() {
  // platform
  const { isMobile } = usePlatformOS();

  return (
    <Tooltip tooltipContent={`Version: v${packageJson.version}`} isMobile={isMobile}>
      <Badge variant="neutral" size="lg">
        v{packageJson.version}
      </Badge>
    </Tooltip>
  );
});
