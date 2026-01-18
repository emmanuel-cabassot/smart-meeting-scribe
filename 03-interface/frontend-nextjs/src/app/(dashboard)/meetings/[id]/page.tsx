"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Clock, Users, AlertCircle, Loader2 } from "lucide-react";

import { useTranscript } from "@/hooks/use-transcript";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format timestamp in seconds to MM:SS format
 */
function formatTimestamp(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

/**
 * Format date for display
 */
function formatDate(dateString: string | null): string {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

/**
 * Get speaker badge color based on speaker name
 */
function getSpeakerColor(speaker: string): string {
    // Simple hash-based color selection
    const colors = [
        "bg-blue-500/20 text-blue-400 border-blue-500/30",
        "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        "bg-amber-500/20 text-amber-400 border-amber-500/30",
        "bg-violet-500/20 text-violet-400 border-violet-500/30",
        "bg-pink-500/20 text-pink-400 border-pink-500/30",
        "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
    ];

    let hash = 0;
    for (let i = 0; i < speaker.length; i++) {
        hash = speaker.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}

// ============================================================================
// LOADING SKELETON
// ============================================================================

function TranscriptSkeleton() {
    return (
        <div className="space-y-6">
            {/* Header skeleton */}
            <div className="space-y-2">
                <Skeleton className="h-8 w-2/3 bg-bg-hover" />
                <Skeleton className="h-4 w-1/3 bg-bg-hover" />
            </div>

            {/* Segments skeleton */}
            <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex gap-4">
                        <Skeleton className="h-5 w-12 bg-bg-hover shrink-0" />
                        <div className="flex-1 space-y-2">
                            <Skeleton className="h-4 w-20 bg-bg-hover" />
                            <Skeleton className="h-4 w-full bg-bg-hover" />
                            <Skeleton className="h-4 w-4/5 bg-bg-hover" />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ============================================================================
// MAIN PAGE COMPONENT
// ============================================================================

export default function MeetingDetailPage() {
    const params = useParams();
    const router = useRouter();

    const meetingId = params.id ? parseInt(params.id as string, 10) : null;
    const { transcript, isLoading, error } = useTranscript(meetingId);

    // Group segments by speaker for visual grouping
    const speakerColors = new Map<string, string>();
    if (transcript?.segments) {
        const uniqueSpeakers = [...new Set(transcript.segments.map((s) => s.speaker))];
        uniqueSpeakers.forEach((speaker) => {
            speakerColors.set(speaker, getSpeakerColor(speaker));
        });
    }

    return (
        <div className="space-y-6">
            {/* Back navigation */}
            <div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => router.back()}
                    className="text-text-secondary hover:text-text-primary"
                >
                    <ArrowLeft className="mr-2 size-4" />
                    Back to Dashboard
                </Button>
            </div>

            {/* Error state */}
            {error && (
                <Card className="border-status-failed/20 bg-status-failed/5">
                    <CardContent className="flex flex-col items-center justify-center py-12">
                        <AlertCircle className="size-12 text-status-failed mb-4" />
                        <h2 className="text-lg font-semibold text-text-primary mb-2">
                            Failed to load transcript
                        </h2>
                        <p className="text-text-secondary text-center mb-4">
                            {error.message}
                        </p>
                        <Button variant="outline" onClick={() => router.back()}>
                            Go back
                        </Button>
                    </CardContent>
                </Card>
            )}

            {/* Loading state */}
            {isLoading && !error && (
                <Card className="border-border-subtle bg-bg-secondary">
                    <CardContent className="py-8">
                        <TranscriptSkeleton />
                    </CardContent>
                </Card>
            )}

            {/* Transcript content */}
            {!isLoading && !error && transcript && (
                <>
                    {/* Meeting header */}
                    <Card className="border-border-subtle bg-bg-secondary">
                        <CardHeader className="pb-4">
                            <div className="flex items-start justify-between gap-4">
                                <div className="space-y-2">
                                    <h1 className="text-2xl font-bold text-text-primary">
                                        {transcript.title}
                                    </h1>
                                    <div className="flex items-center gap-4 text-text-secondary text-sm">
                                        <span className="flex items-center gap-1.5">
                                            <Clock className="size-4" />
                                            {formatDate(transcript.created_at)}
                                        </span>
                                        <span className="flex items-center gap-1.5">
                                            <Users className="size-4" />
                                            {speakerColors.size} speaker{speakerColors.size > 1 ? "s" : ""}
                                        </span>
                                    </div>
                                </div>
                                <Badge
                                    variant="outline"
                                    className="bg-status-completed/20 text-status-completed border-status-completed/30"
                                >
                                    {transcript.status}
                                </Badge>
                            </div>

                            {/* Speaker legend */}
                            <div className="flex flex-wrap gap-2 mt-4">
                                {Array.from(speakerColors.entries()).map(([speaker, color]) => (
                                    <Badge
                                        key={speaker}
                                        variant="outline"
                                        className={color}
                                    >
                                        {speaker}
                                    </Badge>
                                ))}
                            </div>
                        </CardHeader>
                    </Card>

                    {/* Transcript segments */}
                    <Card className="border-border-subtle bg-bg-secondary">
                        <CardHeader>
                            <h2 className="text-lg font-semibold text-text-primary">
                                Transcript
                            </h2>
                            <p className="text-text-secondary text-sm">
                                {transcript.segments.length} segments
                            </p>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {transcript.segments.map((segment, index) => (
                                <div
                                    key={index}
                                    className="flex gap-4 py-3 border-b border-border-subtle last:border-0"
                                >
                                    {/* Timestamp */}
                                    <span className="text-xs text-text-muted font-mono shrink-0 pt-0.5">
                                        {formatTimestamp(segment.start)}
                                    </span>

                                    {/* Content */}
                                    <div className="flex-1 space-y-1">
                                        <Badge
                                            variant="outline"
                                            className={`text-xs ${speakerColors.get(segment.speaker) || ""}`}
                                        >
                                            {segment.speaker}
                                        </Badge>
                                        <p className="text-text-primary text-sm leading-relaxed">
                                            {segment.text}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    );
}
