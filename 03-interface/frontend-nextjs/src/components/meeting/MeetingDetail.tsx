"use client";

import { useState, useMemo, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { MeetingToolbar } from "./MeetingToolbar";
import { MeetingHeader } from "./MeetingHeader";
import { TranscriptView } from "./TranscriptView";
import { formatTime, SPEAKER_COLORS, AVATAR_COLORS } from "./transcript-utils";
import { TranscriptResponse } from "@/hooks/use-transcript";

interface MeetingDetailProps {
    transcript: TranscriptResponse;
}

export function MeetingDetail({ transcript }: MeetingDetailProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [viewMode, setViewMode] = useState<"detailed" | "grouped">("grouped");

    // Assign deterministic colors to speakers
    const { speakerColors, speakerAvatarColors } = useMemo(() => {
        const uniqueSpeakers = Array.from(new Set(transcript.segments.map(s => s.speaker))).sort();
        const colorsMap = new Map<string, string>();
        const avatarsMap = new Map<string, string>();

        uniqueSpeakers.forEach((speaker, index) => {
            colorsMap.set(speaker, SPEAKER_COLORS[index % SPEAKER_COLORS.length]);
            avatarsMap.set(speaker, AVATAR_COLORS[index % AVATAR_COLORS.length]);
        });

        return { speakerColors: colorsMap, speakerAvatarColors: avatarsMap };
    }, [transcript]);

    // Calculate speaker statistics
    const speakerStats = useMemo(() => {
        const stats: Record<string, number> = {};

        for (const segment of transcript.segments) {
            const duration = segment.end - segment.start;
            stats[segment.speaker] = (stats[segment.speaker] || 0) + duration;
        }

        const totalDuration = Object.values(stats).reduce((a, b) => a + b, 0);

        return Object.entries(stats)
            .map(([speaker, duration]) => ({
                speaker,
                duration,
                percentage: totalDuration > 0 ? (duration / totalDuration) * 100 : 0,
            }))
            .sort((a, b) => b.duration - a.duration);
    }, [transcript]);

    // Get filtered segments for export
    const getExportText = useCallback(() => {
        const filteredSegments = searchQuery
            ? transcript.segments.filter((s) =>
                s.text.toLowerCase().includes(searchQuery.toLowerCase())
            )
            : transcript.segments;

        const dateStr = transcript.created_at || new Date().toISOString();
        const header = `${transcript.title}\nDate: ${new Date(dateStr).toLocaleString()}\n\n`;
        const content = filteredSegments
            .map((s) => `[${formatTime(s.start)}] ${s.speaker}: ${s.text}`)
            .join("\n");

        return header + content;
    }, [searchQuery, transcript]);

    const handleCopy = useCallback(async () => {
        const text = getExportText();
        // Use try/catch for clipboard operations
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            console.error("Failed to copy transcript:", err);
        }
    }, [getExportText]);

    const handleDownload = useCallback(() => {
        const text = getExportText();
        const blob = new Blob([text], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${(transcript.title || "meeting").replace(/\s+/g, "_")}_transcript.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, [getExportText, transcript]);

    return (
        <div className="min-h-screen bg-bg-primary">
            <Card className="max-w-4xl mx-auto my-0 sm:my-6 border-border-subtle bg-bg-secondary rounded-none sm:rounded-lg overflow-hidden">
                <MeetingToolbar
                    searchQuery={searchQuery}
                    onSearchChange={setSearchQuery}
                    viewMode={viewMode}
                    onViewModeChange={setViewMode}
                    speakerStats={speakerStats}
                    onCopy={handleCopy}
                    onDownload={handleDownload}
                />
                <MeetingHeader transcript={transcript} speakerColors={speakerColors} />
                <TranscriptView
                    segments={transcript.segments}
                    viewMode={viewMode}
                    searchQuery={searchQuery}
                    speakerColors={speakerColors}
                    speakerAvatarColors={speakerAvatarColors}
                />
            </Card>
        </div>
    );
}
