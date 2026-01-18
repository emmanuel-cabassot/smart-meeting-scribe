"use client";

import { Clock, FileText, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { formatTime } from "./transcript-utils";
import { TranscriptResponse } from "@/hooks/use-transcript";

interface MeetingHeaderProps {
    transcript: TranscriptResponse;
    speakerColors?: Map<string, string>;
}

export function MeetingHeader({ transcript, speakerColors }: MeetingHeaderProps) {
    const dateString = transcript.created_at || new Date().toISOString();
    const displayDate = new Date(dateString);

    const formattedDate = displayDate.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    const formattedTime = displayDate.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
    });

    // Calculate duration from segments if available, otherwise 0
    const duration = transcript.segments.length > 0
        ? transcript.segments[transcript.segments.length - 1].end - transcript.segments[0].start
        : 0;

    return (
        <div className="px-4 py-6 sm:px-6 border-b border-border">
            <div className="space-y-4">
                <div className="flex items-start justify-between gap-4">
                    <h1 className="text-xl sm:text-2xl font-semibold text-foreground tracking-tight text-balance">
                        {transcript.title || "Untitled Meeting"}
                    </h1>
                    <Badge
                        variant={transcript.status === "completed" ? "default" : "secondary"}
                        className={
                            transcript.status === "completed"
                                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30"
                                : ""
                        }
                    >
                        {transcript.status.charAt(0).toUpperCase() + transcript.status.slice(1)}
                    </Badge>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                        <Calendar className="h-4 w-4" />
                        <span>{formattedDate}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <FileText className="h-4 w-4" />
                        <span>{formattedTime}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <Clock className="h-4 w-4" />
                        <span>{formatTime(duration)}</span>
                    </div>
                </div>

                {/* Speaker Legend */}
                {speakerColors && speakerColors.size > 0 && (
                    <div className="flex flex-wrap gap-2 pt-2">
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
                )}
            </div>
        </div>
    );
}
