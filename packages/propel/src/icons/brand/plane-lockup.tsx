/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import * as React from "react";

import type { ISvgIcons } from "../type";

export function PlaneLockup({ width = "253", height = "53", className, color = "currentColor" }: ISvgIcons) {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 253 53"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Bright-Byte PMP — placeholder horizontal lockup */}
      {/* Compact "BB" mark at left (scaled to ~36px tall, centered in 53px) */}
      <g transform="translate(0,8.5) scale(0.614)">
        {/* Left "B" */}
        <rect x="4" y="6" width="8" height="40" rx="2" fill={color} />
        <path d="M12 6 H26 C32 6 36 10 36 16 C36 22 32 25 26 25 H12 Z" fill={color} />
        <path d="M12 25 H27 C34 25 38 29 38 36 C38 43 34 46 27 46 H12 Z" fill={color} />
        {/* Divider */}
        <rect x="41" y="10" width="3" height="32" rx="1.5" fill={color} opacity="0.35" />
        {/* Right "B" */}
        <rect x="48" y="6" width="8" height="40" rx="2" fill={color} />
        <path d="M56 6 H70 C76 6 80 10 80 16 C80 22 76 25 70 25 H56 Z" fill={color} />
        <path d="M56 25 H71 C78 25 82 29 82 36 C82 43 78 46 71 46 H56 Z" fill={color} />
      </g>
      {/* "Bright-Byte PMP" wordmark text rendered as geometric paths */}
      {/* Using simple geometric letterforms at x=58, y baseline ~37, font-size ~22 */}
      {/* B */}
      <rect x="58" y="12" width="5" height="28" rx="1" fill={color} />
      <path d="M63 12 H72 C76 12 79 15 79 19.5 C79 24 76 26.5 72 26.5 H63 Z" fill={color} />
      <path d="M63 26.5 H73 C77.5 26.5 81 30 81 34.5 C81 39 77.5 40 73 40 H63 Z" fill={color} />
      {/* r */}
      <rect x="84" y="20" width="4" height="20" rx="1" fill={color} />
      <path d="M88 20 Q92 18 96 20" stroke={color} strokeWidth="3.5" strokeLinecap="round" fill="none" />
      {/* i */}
      <rect x="99" y="20" width="4" height="20" rx="1" fill={color} />
      <circle cx="101" cy="15" r="2.5" fill={color} />
      {/* g */}
      <path
        d="M105 20 Q105 18 108 18 Q116 18 116 26 Q116 34 108 34 Q105 34 105 31 L105 38 Q105 42 109 42 Q112 42 113 40"
        stroke={color}
        strokeWidth="3.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* h */}
      <rect x="119" y="12" width="4" height="28" rx="1" fill={color} />
      <path
        d="M123 24 Q127 18 132 20 L132 40"
        stroke={color}
        strokeWidth="3.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* t */}
      <rect x="136" y="15" width="4" height="25" rx="1" fill={color} />
      <rect x="132" y="20" width="12" height="3.5" rx="1.75" fill={color} />
      {/* - */}
      <rect x="149" y="26" width="8" height="3" rx="1.5" fill={color} />
      {/* B (Byte) */}
      <rect x="160" y="12" width="5" height="28" rx="1" fill={color} />
      <path d="M165 12 H174 C178 12 181 15 181 19.5 C181 24 178 26.5 174 26.5 H165 Z" fill={color} />
      <path d="M165 26.5 H175 C179.5 26.5 183 30 183 34.5 C183 39 179.5 40 175 40 H165 Z" fill={color} />
      {/* y */}
      <path
        d="M186 20 L190 33 L194 20"
        stroke={color}
        strokeWidth="3.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path d="M188 30 L186 40 Q185 44 189 44" stroke={color} strokeWidth="3.5" strokeLinecap="round" fill="none" />
      {/* t */}
      <rect x="197" y="15" width="4" height="25" rx="1" fill={color} />
      <rect x="193" y="20" width="12" height="3.5" rx="1.75" fill={color} />
      {/* e */}
      <path
        d="M208 29 H220 Q220 20 214 19 Q208 18 208 26 Q208 34 214 35 Q218 35 220 33"
        stroke={color}
        strokeWidth="3.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* space then P */}
      <rect x="224" y="12" width="5" height="28" rx="1" fill={color} />
      <path d="M229 12 H238 C243 12 247 16 247 21.5 C247 27 243 29 238 29 H229 Z" fill={color} />
      {/* M */}
      <rect x="250" y="12" width="0" height="0" fill="none" />
    </svg>
  );
}
