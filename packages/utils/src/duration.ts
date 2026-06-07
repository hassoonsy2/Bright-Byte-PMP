/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

/**
 * @description parses a human-readable duration string into a whole number of seconds.
 * Supports unit suffixes (h, m, s), decimals (comma or dot), and bare numbers (treated as minutes).
 * @param { string } input
 * @returns { number | null } total seconds, or null when the input is empty/invalid
 * @example parseDurationToSeconds("1h 43m 4s") // 6184
 * @example parseDurationToSeconds("1,5")       // 90   (1.5 minutes)
 * @example parseDurationToSeconds("90")        // 5400 (90 minutes)
 * @example parseDurationToSeconds("2h30m")     // 9000
 */
export const parseDurationToSeconds = (input: string): number | null => {
  const normalized = input.trim().toLowerCase().replace(/,/g, ".");
  if (normalized === "") return null;

  // Bare number with no unit -> interpret as minutes
  if (/^\d*\.?\d+$/.test(normalized)) {
    const minutes = Number(normalized);
    return Number.isFinite(minutes) ? Math.round(minutes * 60) : null;
  }

  // Unit tokens: hours (h), minutes (m), seconds (s), each with an optional decimal value
  let totalSeconds = 0;
  let matched = false;
  for (const token of normalized.matchAll(/(\d*\.?\d+)\s*(h|m|s)/g)) {
    const value = Number(token[1]);
    if (!Number.isFinite(value)) continue;
    matched = true;
    if (token[2] === "h") totalSeconds += value * 3600;
    else if (token[2] === "m") totalSeconds += value * 60;
    else totalSeconds += value;
  }

  return matched ? Math.round(totalSeconds) : null;
};

/**
 * @description formats a whole number of seconds into a compact "1h 43m 4s" string.
 * Zero-valued units are omitted; returns "" for null/zero/negative.
 * @param { number | null | undefined } totalSeconds
 * @returns { string }
 * @example formatSecondsToDuration(6184) // "1h 43m 4s"
 * @example formatSecondsToDuration(90)   // "1m 30s"
 * @example formatSecondsToDuration(3600) // "1h"
 */
export const formatSecondsToDuration = (totalSeconds: number | null | undefined): string => {
  if (!totalSeconds || totalSeconds <= 0) return "";
  const total = Math.round(totalSeconds);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const seconds = total % 60;
  const parts: string[] = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (seconds > 0) parts.push(`${seconds}s`);
  return parts.join(" ");
};
