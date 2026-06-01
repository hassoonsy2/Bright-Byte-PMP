/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API, FileInfo, Options } from "jscodeshift";

type StringNode = {
  type?: string;
  value?: unknown;
};

type SourceNode = {
  source?: StringNode | null;
};

type CallNode = {
  callee?: unknown;
  arguments?: unknown[];
};

const OLD_SCOPE = ["@plane", ""].join("/");
const NEW_SCOPE = ["@bright-byte", ""].join("/");

function renamedSpecifier(value: string) {
  if (!value.startsWith(OLD_SCOPE)) {
    return value;
  }

  return `${NEW_SCOPE}${value.slice(OLD_SCOPE.length)}`;
}

function renameStringNode(node: StringNode | null | undefined) {
  if (!node || typeof node.value !== "string") {
    return false;
  }

  const nextValue = renamedSpecifier(node.value);
  if (nextValue === node.value) {
    return false;
  }

  node.value = nextValue;
  return true;
}

function isRequireCall(node: CallNode) {
  const callee = node.callee as { type?: string; name?: string } | undefined;
  return callee?.type === "Identifier" && callee.name === "require";
}

function isDynamicImportCall(node: CallNode) {
  const callee = node.callee as { type?: string } | undefined;
  return callee?.type === "Import";
}

export default function transform(
  file: FileInfo,
  api: API,
  options: Options
) {
  const j = api.jscodeshift;
  const root = j(file.source);

  root.find(j.ImportDeclaration).forEach((path) => {
    renameStringNode((path.node as SourceNode).source);
  });

  root.find(j.ExportNamedDeclaration).forEach((path) => {
    renameStringNode((path.node as SourceNode).source);
  });

  root.find(j.ExportAllDeclaration).forEach((path) => {
    renameStringNode((path.node as SourceNode).source);
  });

  root.find(j.CallExpression).forEach((path) => {
    const node = path.node as CallNode;

    if (!isRequireCall(node) && !isDynamicImportCall(node)) {
      return;
    }

    renameStringNode(node.arguments?.[0] as StringNode | undefined);
  });

  return root.toSource(options);
}
