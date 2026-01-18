"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";

export interface TranscriptSegment {
    start: number;
    end: number;
    text: string;
    speaker: string;
}

export interface TranscriptResponse {
    meeting_id: number;
    title: string;
    status: string;
    created_at: string | null;
    segments: TranscriptSegment[];
}

/**
 * Hook to fetch transcript for a specific meeting
 */
export function useTranscript(meetingId: number | null) {
    const [transcript, setTranscript] = useState<TranscriptResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchTranscript = useCallback(async () => {
        if (!meetingId) {
            setIsLoading(false);
            return;
        }

        try {
            setIsLoading(true);
            setError(null);
            const data = await api.get<TranscriptResponse>(`/meetings/${meetingId}/transcript`);
            setTranscript(data);
        } catch (err) {
            setError(err instanceof Error ? err : new Error("Failed to fetch transcript"));
            console.error("Error fetching transcript:", err);
        } finally {
            setIsLoading(false);
        }
    }, [meetingId]);

    useEffect(() => {
        fetchTranscript();
    }, [fetchTranscript]);

    return {
        transcript,
        isLoading,
        error,
        refetch: fetchTranscript,
    };
}
