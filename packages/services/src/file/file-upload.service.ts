/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import axios, { CancelToken, isCancel } from "axios";
// api service
import { APIService } from "../api.service";

/**
 * Service class for handling file upload operations
 * Handles file uploads
 * @extends {APIService}
 */
export class FileUploadService extends APIService {
  private cancelSource: any;

  constructor() {
    super("");
  }

  /**
   * Uploads a file to the specified presigned URL via PUT.
   * R2 does not support S3 POST Object, so uploads use a presigned PUT of the
   * raw file (works on R2, AWS S3, and MinIO).
   * @param {string} url - The presigned PUT URL to upload the file to
   * @param {File} data - The file to upload
   * @returns {Promise<void>} Promise resolving to void
   * @throws {Error} If the request fails
   */
  async uploadFile(url: string, data: File): Promise<void> {
    this.cancelSource = CancelToken.source();
    return axios
      .put(url, data, {
        headers: {
          "Content-Type": data.type || "application/octet-stream",
        },
        cancelToken: this.cancelSource.token,
        withCredentials: false,
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

  /**
   * Cancels the upload
   */
  cancelUpload() {
    this.cancelSource.cancel("Upload canceled");
  }
}
