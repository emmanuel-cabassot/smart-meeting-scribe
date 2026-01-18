import { useAuthStore } from "@/stores/auth-store";

// API Base URL - Uses environment variable for browser-side requests
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Error types
export class ApiError extends Error {
    constructor(
        public status: number,
        public statusText: string,
        public data?: unknown
    ) {
        super(`${status}: ${statusText}`);
        this.name = "ApiError";
    }
}

// Helper to get auth header
function getAuthHeaders(): HeadersInit {
    const token = useAuthStore.getState().token;
    if (token) {
        return {
            Authorization: `Bearer ${token}`,
        };
    }
    return {};
}

// Core fetch wrapper
async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}/api/v1${endpoint}`;

    const headers: Record<string, string> = {
        ...(getAuthHeaders() as Record<string, string>),
        ...(options.headers as Record<string, string>),
    };

    // Add Content-Type for JSON body (but not for FormData)
    if (options.body && !(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    // Handle 401 Unauthorized - Logout user
    if (response.status === 401) {
        useAuthStore.getState().logout();
        // Optionally redirect to login
        if (typeof window !== "undefined") {
            window.location.href = "/login";
        }
        throw new ApiError(401, "Non authentifié");
    }

    // Handle other errors
    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = null;
        }
        throw new ApiError(response.status, response.statusText, errorData);
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return undefined as T;
    }

    return response.json();
}

// HTTP method helpers
export const api = {
    get: <T>(endpoint: string) => fetchApi<T>(endpoint, { method: "GET" }),

    post: <T>(endpoint: string, body?: unknown) =>
        fetchApi<T>(endpoint, {
            method: "POST",
            body: body instanceof FormData ? body : JSON.stringify(body),
        }),

    patch: <T>(endpoint: string, body: unknown) =>
        fetchApi<T>(endpoint, {
            method: "PATCH",
            body: JSON.stringify(body),
        }),

    delete: <T>(endpoint: string) => fetchApi<T>(endpoint, { method: "DELETE" }),

    // Special method for form-data (login)
    postForm: <T>(endpoint: string, formData: FormData) =>
        fetchApi<T>(endpoint, {
            method: "POST",
            body: formData,
        }),
};

// Upload with progress tracking
export async function uploadWithProgress(
    endpoint: string,
    formData: FormData,
    onProgress: (progress: number) => void
): Promise<unknown> {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const url = `${API_BASE_URL}/api/v1${endpoint}`;

        xhr.upload.addEventListener("progress", (event) => {
            if (event.lengthComputable) {
                const progress = Math.round((event.loaded / event.total) * 100);
                onProgress(progress);
            }
        });

        xhr.addEventListener("load", () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    resolve(JSON.parse(xhr.responseText));
                } catch {
                    resolve(xhr.responseText);
                }
            } else if (xhr.status === 401) {
                useAuthStore.getState().logout();
                if (typeof window !== "undefined") {
                    window.location.href = "/login";
                }
                reject(new ApiError(401, "Non authentifié"));
            } else {
                reject(new ApiError(xhr.status, xhr.statusText));
            }
        });

        xhr.addEventListener("error", () => {
            reject(new Error("Erreur réseau"));
        });

        xhr.addEventListener("abort", () => {
            reject(new Error("Upload annulé"));
        });

        xhr.open("POST", url);

        // Add auth header
        const token = useAuthStore.getState().token;
        if (token) {
            xhr.setRequestHeader("Authorization", `Bearer ${token}`);
        }

        xhr.send(formData);
    });
}

export default api;
