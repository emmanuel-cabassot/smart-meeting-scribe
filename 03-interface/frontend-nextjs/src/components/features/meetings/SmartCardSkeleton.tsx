"use client";

import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Skeleton loading state for SmartCard
 * Used while meetings are being fetched
 */
export function SmartCardSkeleton() {
    return (
        <Card className="overflow-hidden border-white/[0.08] bg-[#141416]">
            <CardHeader className="gap-1 pb-3">
                <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1 space-y-2">
                        <Skeleton className="h-5 w-3/4 bg-white/[0.05]" />
                        <Skeleton className="h-4 w-1/4 bg-white/[0.05]" />
                    </div>
                    <Skeleton className="size-8 rounded-md bg-white/[0.05]" />
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Badges skeleton */}
                <div className="flex items-center gap-2">
                    <Skeleton className="h-5 w-16 rounded-full bg-white/[0.05]" />
                    <Skeleton className="h-5 w-20 rounded-full bg-white/[0.05]" />
                    <Skeleton className="ml-auto h-5 w-24 rounded-full bg-white/[0.05]" />
                </div>

                {/* AI Summary skeleton */}
                <div className="space-y-2 rounded-lg border border-white/[0.08] bg-white/[0.03] p-4">
                    <Skeleton className="h-4 w-24 bg-white/[0.05]" />
                    <div className="space-y-2">
                        <Skeleton className="h-3 w-full bg-white/[0.05]" />
                        <Skeleton className="h-3 w-5/6 bg-white/[0.05]" />
                        <Skeleton className="h-3 w-4/6 bg-white/[0.05]" />
                    </div>
                </div>

                {/* Audio player skeleton */}
                <div className="flex items-center gap-3">
                    <Skeleton className="size-8 rounded-md bg-white/[0.05]" />
                    <Skeleton className="h-1.5 flex-1 rounded-full bg-white/[0.05]" />
                    <Skeleton className="h-4 w-20 bg-white/[0.05]" />
                </div>
            </CardContent>

            <CardFooter className="gap-2 pt-2">
                <Skeleton className="h-9 flex-1 rounded-md bg-white/[0.05]" />
                <Skeleton className="h-9 flex-1 rounded-md bg-white/[0.05]" />
            </CardFooter>
        </Card>
    );
}
