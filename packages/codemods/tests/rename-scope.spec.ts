/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { describe, expect, it } from "vitest";
import { applyTransform } from "@hypermod/utils";
import * as transformer from "../rename-scope";

const oldPackage = (name: string) => ["@plane", name].join("/");

async function transform(source: string) {
  return applyTransform(transformer, source, { parser: "tsx" });
}

describe("rename-scope", () => {
  it("rewrites import declarations", async () => {
    const result = await transform(`
      import { Button } from "${oldPackage("ui")}";
      import type { TIssue } from "${oldPackage("types")}";
      import "${oldPackage("editor/styles.css")}";
    `);

    expect(result).toContain(`from "@bright-byte/ui"`);
    expect(result).toContain(`from "@bright-byte/types"`);
    expect(result).toContain(`import "@bright-byte/editor/styles.css"`);
  });

  it("rewrites export declarations", async () => {
    const result = await transform(`
      export { Button } from "${oldPackage("ui")}";
      export type { TIssue } from "${oldPackage("types")}";
      export * from "${oldPackage("hooks")}";
    `);

    expect(result).toContain(`from "@bright-byte/ui"`);
    expect(result).toContain(`from "@bright-byte/types"`);
    expect(result).toContain(`from "@bright-byte/hooks"`);
  });

  it("rewrites dynamic imports, require calls, and package subpaths", async () => {
    const result = await transform(`
      const editor = import("${oldPackage("editor/extensions")}");
      const button = require("${oldPackage("propel/button")}");
    `);

    expect(result).toContain(`import("@bright-byte/editor/extensions")`);
    expect(result).toContain(`require("@bright-byte/propel/button")`);
  });

  it("preserves edition aliases and arbitrary strings", async () => {
    const result = await transform(`
      import { Root } from "@/plane-web/app";
      import { Live } from "@/plane-live/app";

      const packageName = "${oldPackage("ui")}";
      const route = "/plane-web/settings";
    `);

    expect(result).toContain(`from "@/plane-web/app"`);
    expect(result).toContain(`from "@/plane-live/app"`);
    expect(result).toContain(`const packageName = "${oldPackage("ui")}";`);
    expect(result).toContain(`const route = "/plane-web/settings";`);
  });
});
