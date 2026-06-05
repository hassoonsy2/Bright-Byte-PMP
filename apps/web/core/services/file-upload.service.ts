/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { AxiosRequestConfig } from "axios";
import axios, { CancelToken, isCancel } from "axios";
// services
import { APIService } from "@/services/api.service";

export class FileUploadService extends APIService {
  private cancelSource: any;

  constructor() {
    super("");
  }

  async uploadFile(
    url: string,
    data: File,
    uploadProgressHandler?: AxiosRequestConfig["onUploadProgress"]
  ): Promise<void> {
    // R2 does not support S3 POST Object, so uploads use a presigned PUT of the
    // raw file (works on R2, AWS S3, and MinIO).
    this.cancelSource = CancelToken.source();
    return axios
      .put(url, data, {
        headers: {
          "Content-Type": data.type || "application/octet-stream",
        },
        cancelToken: this.cancelSource.token,
        withCredentials: false,
        onUploadProgress: uploadProgressHandler,
      })
      .then((response) => response?.data)
      .catch((error) => {
        if (isCancel(error)) {
          console.log(error.message);
        } else {
          throw error?.response?.data;
        }
      });
  }

  cancelUpload() {
    this.cancelSource.cancel("Upload canceled");
  }
}
