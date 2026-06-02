/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import * as React from "react";

import type { ISvgIcons } from "../type";

export function PlaneLogo({ width = "85", height = "52", className, color = "currentColor" }: ISvgIcons) {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 85 52"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Bright-Byte PMP — placeholder compact "BB" lettermark */}
      {/* Left "B" */}
      <rect x="4" y="6" width="8" height="40" rx="2" fill={color} />
      <path d="M12 6 H26 Q36 6 36 17 Q36 23 29 25 Q38 27 38 37 Q38 46 26 46 H12 Z" fill={color} />
      <rect x="12" y="6" width="14" height="19" rx="7" fill="none" stroke={color} strokeWidth="0" />
      <path d="M12 6 H26 C32 6 36 10 36 16 C36 22 32 25 26 25 H12 Z" fill={color} />
      <path d="M12 25 H27 C34 25 38 29 38 36 C38 43 34 46 27 46 H12 Z" fill={color} />
      {/* Divider */}
      <rect x="41" y="10" width="3" height="32" rx="1.5" fill={color} opacity="0.35" />
      {/* Right "B" */}
      <rect x="48" y="6" width="8" height="40" rx="2" fill={color} />
      <path d="M56 6 H70 C76 6 80 10 80 16 C80 22 76 25 70 25 H56 Z" fill={color} />
      <path d="M56 25 H71 C78 25 82 29 82 36 C82 43 78 46 71 46 H56 Z" fill={color} />
    </svg>
  );
}
