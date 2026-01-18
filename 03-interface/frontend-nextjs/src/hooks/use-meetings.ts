"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { Meeting } from "@/types/meeting";

/**
 * Hook to fetch and manage meetings from the API
 * TODO: Migrate to React Query for better caching and refetching
 */
export function useMeetings() {
    const [meetings, setMeetings] = useState<Meeting[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchMeetings = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await api.get<Meeting[]>("/meetings/");
            setMeetings(data);
        } catch (err) {
            setError(err instanceof Error ? err : new Error("Failed to fetch meetings"));
            console.error("Error fetching meetings:", err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchMeetings();
    }, [fetchMeetings]);

    const refetch = useCallback(() => {
        fetchMeetings();
    }, [fetchMeetings]);

    return {
        meetings,
        isLoading,
        error,
        refetch,
    };
}
