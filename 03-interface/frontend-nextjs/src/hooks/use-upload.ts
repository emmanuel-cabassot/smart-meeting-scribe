import { useState } from "react";

interface UploadOptions {
    url: string;
    file: File;
}

interface UploadResponse {
    status: string;
    meeting_id: string;
    task_id: string;
    s3_path: string;
    message: string;
}

export function useXHRUpload() {
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
    const [error, setError] = useState<string | null>(null);

    const upload = ({ url, file }: UploadOptions): Promise<UploadResponse | null> => {
        return new Promise((resolve, reject) => {
            setStatus("uploading");
            setProgress(0);
            setError(null);

            const xhr = new XMLHttpRequest();
            const formData = new FormData();
            formData.append("file", file);

            // Progression de l'upload
            xhr.upload.addEventListener("progress", (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    setProgress(percent);
                }
            });

            // Fin de l'upload
            xhr.addEventListener("load", () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    setStatus("success");
                    setProgress(100);
                    try {
                        const response = JSON.parse(xhr.responseText) as UploadResponse;
                        resolve(response);
                    } catch {
                        resolve(null);
                    }
                } else {
                    setStatus("error");
                    try {
                        const resp = JSON.parse(xhr.responseText);
                        setError(resp.detail || "Erreur serveur");
                    } catch {
                        setError(`Erreur HTTP ${xhr.status}`);
                    }
                    reject(new Error("Upload failed"));
                }
            });

            // Erreur réseau
            xhr.addEventListener("error", () => {
                setStatus("error");
                setError("Erreur réseau");
                reject(new Error("Network error"));
            });

            xhr.open("POST", url);
            xhr.send(formData);
        });
    };

    const reset = () => {
        setStatus("idle");
        setProgress(0);
        setError(null);
    };

    return { upload, progress, status, error, reset };
}
