/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

// Fixed 32-character test secret matching production token format
// NOTE: This literal is duplicated in vi.mock factories below because vi.mock is hoisted
const TEST_SECRET = "test-secret-key-fixed-length-32c";

// Track timingSafeEqual calls for the RED→GREEN spy test
const mockTimingSafeEqual = vi.fn((a: Buffer, b: Buffer): boolean => {
  // Delegate to real comparison semantics so other tests still work
  if (a.length !== b.length) throw new RangeError("Input buffers must have the same byte length");
  return a.equals(b);
});

// Mock node:crypto so we can spy on timingSafeEqual
vi.mock("node:crypto", () => ({
  timingSafeEqual: mockTimingSafeEqual,
}));

// Mock @bright-byte/logger to prevent side-effects
vi.mock("@bright-byte/logger", () => ({
  logger: {
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    debug: vi.fn(),
  },
}));

// Mock @/env to supply a controlled LIVE_SERVER_SECRET_KEY
// Uses a literal (not TEST_SECRET) because vi.mock factories are hoisted to top of file
vi.mock("@/env", () => ({
  env: {
    LIVE_SERVER_SECRET_KEY: "test-secret-key-fixed-length-32c",
  },
}));

import { requireSecretKey } from "@/lib/auth-middleware";

function makeReq(secretKeyHeader?: string | string[]): Parameters<typeof requireSecretKey>[0] {
  return {
    headers: secretKeyHeader !== undefined ? { "live-server-secret-key": secretKeyHeader } : {},
    path: "/test",
    method: "GET",
    ip: "127.0.0.1",
  } as Parameters<typeof requireSecretKey>[0];
}

function makeRes(): Parameters<typeof requireSecretKey>[1] {
  const res = {
    status: vi.fn(),
    json: vi.fn(),
  };
  res.status.mockReturnValue(res);
  return res as unknown as Parameters<typeof requireSecretKey>[1];
}

describe("auth-middleware — requireSecretKey", () => {
  let next: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    next = vi.fn();
    vi.clearAllMocks();
    // Restore mock implementation after clearAllMocks resets it
    mockTimingSafeEqual.mockImplementation((a: Buffer, b: Buffer): boolean => {
      if (a.length !== b.length) throw new RangeError("Input buffers must have the same byte length");
      return a.equals(b);
    });
  });

  it("correct secret → calls next() and does not send a response", () => {
    const req = makeReq(TEST_SECRET);
    const res = makeRes();

    requireSecretKey(req, res, next);

    expect(next).toHaveBeenCalledOnce();
    expect(res.status).not.toHaveBeenCalled();
    expect(res.json).not.toHaveBeenCalled();
  });

  it("wrong-value token with same byte-length → 401 response, next() NOT called", () => {
    // Same length as TEST_SECRET (32 chars), different value
    const wrongValue = "test-secret-key-fixed-length-32X";
    expect(wrongValue.length).toBe(TEST_SECRET.length); // guard: lengths must match

    const req = makeReq(wrongValue);
    const res = makeRes();

    requireSecretKey(req, res, next);

    expect(next).not.toHaveBeenCalled();
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ error: "Unauthorized", status: 401 });
  });

  it("wrong-length token → 401 response, next() NOT called, no RangeError thrown", () => {
    const shortToken = "too-short";
    expect(shortToken.length).not.toBe(TEST_SECRET.length); // guard: lengths must differ

    const req = makeReq(shortToken);
    const res = makeRes();

    // Must NOT throw — the length pre-check must prevent RangeError from timingSafeEqual
    expect(() => requireSecretKey(req, res, next)).not.toThrow();
    expect(next).not.toHaveBeenCalled();
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ error: "Unauthorized", status: 401 });
  });

  it("missing header → 401 response, next() NOT called", () => {
    const req = makeReq(undefined);
    const res = makeRes();

    requireSecretKey(req, res, next);

    expect(next).not.toHaveBeenCalled();
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ error: "Unauthorized", status: 401 });
  });

  it("uses constant-time comparison — timingSafeEqual called for same-length secrets", () => {
    const req = makeReq(TEST_SECRET);
    const res = makeRes();

    requireSecretKey(req, res, next);

    // RED: fails against the current !== implementation (timingSafeEqual never called)
    // GREEN: passes once the implementation uses crypto.timingSafeEqual
    expect(mockTimingSafeEqual).toHaveBeenCalledOnce();
  });
});
