"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { Toaster } from "@/components/ui/toaster";

interface ProvidersProps {
    children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
    // Create a client instance for each session (not shared between requests)
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        // Don't refetch on window focus in development
                        refetchOnWindowFocus: process.env.NODE_ENV === "production",
                        // Retry failed requests once
                        retry: 1,
                        // Consider data stale after 30 seconds
                        staleTime: 30 * 1000,
                    },
                    mutations: {
                        // Show error toasts by default (can be overridden)
                        onError: (error) => {
                            console.error("Mutation error:", error);
                        },
                    },
                },
            })
    );

    return (
        <QueryClientProvider client={queryClient}>
            {children}
            <Toaster />
        </QueryClientProvider>
    );
}
