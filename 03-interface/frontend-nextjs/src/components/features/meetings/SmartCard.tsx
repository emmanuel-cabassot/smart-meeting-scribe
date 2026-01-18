"use client";

import * as React from "react";
import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import {
    Play,
    Pause,
    MoreHorizontal,
    FileText,
    MessageSquare,
    Trash2,
    Pencil,
    Download,
    Loader2,
    RefreshCw,
    Sparkles,
} from "lucide-react";

import { cn } from "@/lib/utils";
import type { Meeting } from "@/types/meeting";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format relative date (e.g., "2 hours ago")
 */
function formatRelativeDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) {
        return "just now";
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? "s" : ""} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? "s" : ""} ago`;
    } else if (diffInSeconds < 604800) {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days > 1 ? "s" : ""} ago`;
    } else {
        return date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
        });
    }
}

/**
 * Format duration in seconds to "MM:SS" format
 */
function formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
}

// ============================================================================
// CONFIGURATION
// Using CSS variables from globals.css for theme support
// ============================================================================

/** Group badge color mapping by type - using design system colors */
const groupTypeColors: Record<string, string> = {
    department: "bg-group-department/20 text-group-department border-group-department/30",
    project: "bg-group-project/20 text-group-project border-group-project/30",
    recurring: "bg-group-recurring/20 text-group-recurring border-group-recurring/30",
};

/** Status badge configurations - using design system colors */
const statusConfig: Record<
    string,
    { label: string; className: string; icon?: React.ReactNode }
> = {
    pending: {
        label: "Transcribing...",
        className: "bg-accent-primary/20 text-accent-primary border-accent-primary/30",
        icon: <Loader2 className="size-3 animate-spin" />,
    },
    processing: {
        label: "Processing",
        className: "bg-status-processing/20 text-status-processing border-status-processing/30",
    },
    completed: {
        label: "Completed",
        className: "bg-status-completed/20 text-status-completed border-status-completed/30",
    },
    failed: {
        label: "Failed",
        className: "bg-status-failed/20 text-status-failed border-status-failed/30",
    },
};

// ============================================================================
// COMPONENT PROPS
// ============================================================================

interface SmartCardProps {
    meeting: Meeting;
    /** Optional: Progress percentage for processing state (0-100) */
    progress?: number;
    onEdit?: (id: number) => void;
    onDelete?: (id: number) => void;
    onRetry?: (id: number) => void;
}

// ============================================================================
// SMART CARD COMPONENT
// ============================================================================

export function SmartCard({
    meeting,
    progress = 0,
    onEdit,
    onDelete,
    onRetry
}: SmartCardProps) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [audioDuration, setAudioDuration] = useState(
        meeting.transcription_result?.duration || 0
    );
    const audioRef = useRef<HTMLAudioElement>(null);

    const status = statusConfig[meeting.status];
    const isCompleted = meeting.status === "completed";
    const isFailed = meeting.status === "failed";
    const isProcessing = meeting.status === "processing";

    // ==========================================================================
    // AUDIO PLAYER CONTROLS
    // ==========================================================================

    const togglePlayPause = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
            } else {
                audioRef.current.play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    const handleTimeUpdate = () => {
        if (audioRef.current) {
            setCurrentTime(audioRef.current.currentTime);
        }
    };

    const handleLoadedMetadata = () => {
        if (audioRef.current) {
            setAudioDuration(audioRef.current.duration);
        }
    };

    const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (audioRef.current) {
            const rect = e.currentTarget.getBoundingClientRect();
            const clickPosition = (e.clientX - rect.left) / rect.width;
            const newTime = clickPosition * audioDuration;
            audioRef.current.currentTime = newTime;
            setCurrentTime(newTime);
        }
    };

    useEffect(() => {
        const audio = audioRef.current;
        if (audio) {
            audio.addEventListener("ended", () => setIsPlaying(false));
            return () => audio.removeEventListener("ended", () => setIsPlaying(false));
        }
    }, []);

    // ==========================================================================
    // AI SUMMARY
    // TODO: Replace with real AI-generated summary when backend supports it
    // The summary should come from meeting.transcription_result.summary
    // For now, we show a fake default summary as placeholder
    // ==========================================================================
    const summaryPoints = React.useMemo(() => {
        if (!isCompleted) {
            return [];
        }

        // TODO: Intégrer le vrai résumé IA quand le backend le supportera
        // Le résumé devrait venir de meeting.transcription_result.summary

        const segments = meeting.transcription_result?.segments || [];

        // If we have segments, show first 2 unique speakers
        if (segments.length > 0) {
            const speakerMessages = new Map<string, string>();
            for (const segment of segments) {
                if (!speakerMessages.has(segment.speaker) && speakerMessages.size < 2) {
                    speakerMessages.set(segment.speaker, segment.text.slice(0, 80));
                }
            }
            return Array.from(speakerMessages.entries()).map(
                ([speaker, text]) => `${speaker}: "${text}${text.length >= 80 ? '...' : ''}"`
            );
        }

        // Fake default summary when no segments available
        return [
            "Meeting transcription completed successfully",
            "Click 'Transcript' to view the full content",
        ];
    }, [isCompleted, meeting.transcription_result]);

    // ==========================================================================
    // AUDIO URL
    // TODO: L'URL audio devrait être une URL signée S3 
    // Pour l'instant, on utilise s3_path directement
    // Le backend devrait exposer un endpoint /meetings/{id}/audio qui retourne
    // une URL signée temporaire pour le streaming
    // ==========================================================================
    const audioUrl = meeting.s3_path || undefined;

    return (
        <Card className="group relative overflow-hidden border-border-subtle bg-bg-secondary transition-all duration-300 hover:border-border-hover hover:shadow-[var(--shadow-glow)]">
            {/* Header: Title + Relative Date */}
            <CardHeader className="gap-0 p-3 pb-2">
                <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                            <h3 className="truncate text-sm font-semibold text-text-primary">
                                {meeting.title}
                            </h3>
                            <span className="text-xs text-text-muted shrink-0">
                                {formatRelativeDate(meeting.created_at)}
                            </span>
                        </div>
                    </div>
                    {/* Dropdown Menu */}
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="shrink-0 size-8 text-text-muted hover:bg-bg-hover hover:text-text-primary"
                            >
                                <MoreHorizontal className="size-4" />
                                <span className="sr-only">Open menu</span>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                            align="end"
                            className="border-border-subtle bg-bg-tertiary"
                        >
                            <DropdownMenuItem
                                onClick={() => onEdit?.(meeting.id)}
                                className="text-text-secondary hover:text-text-primary focus:bg-bg-hover"
                            >
                                <Pencil className="mr-2 size-4" />
                                Edit title
                            </DropdownMenuItem>
                            <DropdownMenuItem className="text-text-secondary hover:text-text-primary focus:bg-bg-hover">
                                <Download className="mr-2 size-4" />
                                Download
                            </DropdownMenuItem>
                            <DropdownMenuSeparator className="bg-border-subtle" />
                            <DropdownMenuItem
                                onClick={() => onDelete?.(meeting.id)}
                                className="text-status-failed focus:bg-status-failed/10 focus:text-status-failed"
                            >
                                <Trash2 className="mr-2 size-4" />
                                Delete
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </CardHeader>

            <CardContent className="space-y-3 px-3 pb-3 pt-0">
                {/* Badges Row: Groups + Status */}
                <div className="flex flex-wrap items-center gap-2">
                    {meeting.groups.map((group) => (
                        <Badge
                            key={group.id}
                            variant="outline"
                            className={cn(
                                "border text-xs font-medium",
                                groupTypeColors[group.type]
                            )}
                        >
                            {group.name}
                        </Badge>
                    ))}
                    <Badge
                        variant="outline"
                        className={cn("ml-auto border text-xs font-medium gap-1", status.className)}
                    >
                        {status.icon}
                        {status.label}
                    </Badge>
                </div>

                {/* Processing State: Progress Bar */}
                {/* TODO: Le progress devrait venir du polling du task_id via l'API */}
                {isProcessing && (
                    <div className="space-y-2">
                        <Progress
                            value={progress}
                            className="h-1.5 bg-bg-hover"
                        />
                        <p className="text-xs text-text-muted">
                            Processing... {progress}%
                        </p>
                    </div>
                )}

                {/* Failed State: Retry Button */}
                {isFailed && (
                    <div className="flex items-center justify-between rounded-md border border-status-failed/20 bg-status-failed/10 px-3 py-2">
                        <p className="text-xs text-status-failed">
                            Transcription failed
                        </p>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onRetry?.(meeting.id)}
                            className="h-7 text-xs text-status-failed hover:bg-status-failed/20"
                        >
                            <RefreshCw className="mr-1.5 size-3" />
                            Retry
                        </Button>
                    </div>
                )}

                {/* AI Summary Section (only if completed) */}
                {/* TODO: Remplacer par le vrai résumé IA quand disponible */}
                {isCompleted && summaryPoints.length > 0 && (
                    <div className="rounded-md border border-border-subtle bg-bg-glass px-3 py-2 backdrop-blur-sm">
                        <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-medium text-accent-primary uppercase tracking-wide">
                            <Sparkles className="size-2.5" />
                            AI Summary
                        </div>
                        <ul className="space-y-1 text-xs text-text-secondary">
                            {summaryPoints.slice(0, 2).map((point, index) => (
                                <li key={index} className="flex items-start gap-1.5">
                                    <span className="mt-1 size-1 shrink-0 rounded-full bg-accent-primary" />
                                    <span className="line-clamp-1">{point}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Audio Player (only if completed and audio available) */}
                {/* TODO: Implémenter un endpoint backend pour générer des URLs signées S3 */}
                {isCompleted && audioUrl && (
                    <div className="space-y-2">
                        <audio
                            ref={audioRef}
                            src={audioUrl}
                            onTimeUpdate={handleTimeUpdate}
                            onLoadedMetadata={handleLoadedMetadata}
                            preload="metadata"
                        />
                        <div className="flex items-center gap-3">
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={togglePlayPause}
                                className="shrink-0 size-8 text-accent-primary hover:bg-accent-primary/20"
                            >
                                {isPlaying ? (
                                    <Pause className="size-4" />
                                ) : (
                                    <Play className="size-4" />
                                )}
                                <span className="sr-only">{isPlaying ? "Pause" : "Play"}</span>
                            </Button>
                            {/* Custom Progress Bar */}
                            <div
                                className="group/progress relative h-1.5 flex-1 cursor-pointer rounded-full bg-border-subtle"
                                onClick={handleProgressClick}
                            >
                                <div
                                    className="absolute inset-y-0 left-0 rounded-full bg-accent-primary transition-all"
                                    style={{
                                        width: `${audioDuration > 0 ? (currentTime / audioDuration) * 100 : 0}%`,
                                    }}
                                />
                                <div
                                    className="absolute top-1/2 size-3 -translate-y-1/2 rounded-full bg-accent-primary opacity-0 shadow-lg transition-opacity group-hover/progress:opacity-100"
                                    style={{
                                        left: `${audioDuration > 0 ? (currentTime / audioDuration) * 100 : 0}%`,
                                        transform: "translate(-50%, -50%)",
                                    }}
                                />
                            </div>
                            <span className="shrink-0 text-xs tabular-nums text-text-muted">
                                {formatDuration(currentTime)} / {formatDuration(audioDuration)}
                            </span>
                        </div>
                    </div>
                )}
            </CardContent>

            {/* Actions Row */}
            <CardFooter className="gap-2 px-3 pb-3 pt-0">
                <Button
                    asChild
                    variant="ghost"
                    size="sm"
                    className="h-7 flex-1 text-xs text-text-secondary hover:bg-accent-primary/10 hover:text-accent-primary"
                >
                    <Link href={`/meetings/${meeting.id}`}>
                        <FileText className="mr-1.5 size-3" />
                        Transcript
                    </Link>
                </Button>
                <Button
                    variant="ghost"
                    size="sm"
                    disabled
                    className="h-7 flex-1 text-xs text-text-muted disabled:opacity-40"
                >
                    <MessageSquare className="mr-1.5 size-3" />
                    Chat
                </Button>
            </CardFooter>
        </Card>
    );
}
