import { useState, useRef, useEffect } from "react";

interface TaskResult {
    status: string;
    meeting_id: string;
    result_path: string;
}

interface Segment {
    speaker: string;
    start: number;
    end: number;
    text: string;
}

interface PollingResponse {
    status: "processing" | "completed" | "error" | "unknown";
    task_id: string;
    result?: Segment[];
    message?: string;
    error?: string;
}

export function usePolling() {
    const [data, setData] = useState<Segment[] | null>(null);
    const [isPolling, setIsPolling] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    const startPolling = (taskId: string) => {
        setIsPolling(true);
        setError(null);
        setData(null);

        const checkStatus = async () => {
            try {
                // URL de l'API (configurable via env)
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
                const res = await fetch(`${API_URL}/api/v1/process/status/${taskId}`);
                if (!res.ok) throw new Error("Erreur serveur");

                const json: PollingResponse = await res.json();

                if (json.status === "completed" && json.result) {
                    setData(json.result);
                    stopPolling();
                } else if (json.status === "error") {
                    setError(json.message || json.error || "Erreur lors du traitement IA");
                    stopPolling();
                }
                // Si "processing" ou "queued", on attend la prochaine boucle
            } catch (err) {
                console.error("Polling error:", err);
                // On continue d'essayer même si une requête échoue
            }
        };

        // Premier check immédiat
        checkStatus();
        // Puis toutes les 2 secondes
        intervalRef.current = setInterval(checkStatus, 2000);
    };

    const stopPolling = () => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
        setIsPolling(false);
    };

    // Cleanup au démontage du composant
    useEffect(() => {
        return () => stopPolling();
    }, []);

    return { data, isPolling, error, startPolling, stopPolling };
}
