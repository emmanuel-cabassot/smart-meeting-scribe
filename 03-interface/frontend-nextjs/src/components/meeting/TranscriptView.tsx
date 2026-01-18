"use client";

import React from "react"
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { formatTime, normalizeText, createSearchRegex } from "./transcript-utils";
import { TranscriptSegment } from "@/hooks/use-transcript";

interface GroupedSegment {
    speaker: string;
    startTime: number;
    endTime: number;
    texts: string[];
}

interface TranscriptViewProps {
    segments: TranscriptSegment[];
    viewMode: "detailed" | "grouped";
    searchQuery: string;
    speakerColors: Map<string, string>;
    speakerAvatarColors: Map<string, string>;
}

function highlightText(text: string, query: string): React.ReactNode {
    if (!query.trim()) return text;

    const regex = createSearchRegex(query);
    const parts = text.split(regex);

    return parts.map((part, i) =>
        regex.test(part) ? (
            <mark key={i} className="bg-accent-warning/40 text-text-primary rounded px-0.5">
                {part}
            </mark>
        ) : (
            part
        )
    );
}

function groupSegments(segments: TranscriptSegment[]): GroupedSegment[] {
    const grouped: GroupedSegment[] = [];

    for (const segment of segments) {
        const lastGroup = grouped[grouped.length - 1];
        if (lastGroup && lastGroup.speaker === segment.speaker) {
            lastGroup.endTime = segment.end;
            lastGroup.texts.push(segment.text);
        } else {
            grouped.push({
                speaker: segment.speaker,
                startTime: segment.start,
                endTime: segment.end,
                texts: [segment.text],
            });
        }
    }

    return grouped;
}

export function TranscriptView({ segments, viewMode, searchQuery, speakerColors, speakerAvatarColors }: TranscriptViewProps) {
    const filteredSegments = searchQuery
        ? segments.filter((s) => normalizeText(s.text).includes(normalizeText(searchQuery)))
        : segments;

    if (viewMode === "detailed") {
        return (
            <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="divide-y divide-border-subtle">
                    {filteredSegments.map((segment, idx) => (
                        <div key={idx} className="p-4 sm:p-6 hover:bg-bg-hover transition-colors rounded-md mx-2 my-1">
                            <div className="flex gap-3 sm:gap-4">
                                <div className="flex-shrink-0">
                                    <Avatar className="h-8 w-8">
                                        <AvatarFallback className={`${speakerAvatarColors.get(segment.speaker)} text-white text-xs font-medium`}>
                                            {segment.speaker.charAt(0).toUpperCase()}
                                        </AvatarFallback>
                                    </Avatar>
                                </div>
                                <div className="flex-1 min-w-0 space-y-1.5">
                                    <div className="flex items-center gap-2 flex-wrap">
                                        <Badge variant="outline" className={`${speakerColors.get(segment.speaker)} text-xs font-medium`}>
                                            {segment.speaker}
                                        </Badge>
                                        <span className="text-xs text-text-secondary font-mono">
                                            {formatTime(segment.start)} - {formatTime(segment.end)}
                                        </span>
                                    </div>
                                    <p className="text-sm text-text-primary leading-relaxed">
                                        {highlightText(segment.text, searchQuery)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                {filteredSegments.length === 0 && (
                    <div className="flex items-center justify-center py-16 text-text-secondary">
                        No matching segments found
                    </div>
                )}
            </ScrollArea>
        );
    }

    // Grouped view
    const groupedData = groupSegments(filteredSegments);

    return (
        <ScrollArea className="h-[calc(100vh-300px)]">
            <div className="divide-y divide-border-subtle">
                {groupedData.map((group, idx) => (
                    <div key={idx} className="p-4 sm:p-6 hover:bg-bg-hover transition-colors rounded-md mx-2 my-1">
                        <div className="flex gap-3 sm:gap-4">
                            <div className="flex-shrink-0">
                                <Avatar className="h-9 w-9">
                                    <AvatarFallback className={`${speakerAvatarColors.get(group.speaker)} text-white text-sm font-medium`}>
                                        {group.speaker.charAt(0).toUpperCase()}
                                    </AvatarFallback>
                                </Avatar>
                            </div>
                            <div className="flex-1 min-w-0 space-y-2">
                                <div className="flex items-center gap-2 flex-wrap">
                                    <Badge variant="outline" className={`${speakerColors.get(group.speaker)} text-xs font-medium`}>
                                        {group.speaker}
                                    </Badge>
                                    <span className="text-xs text-text-secondary font-mono">
                                        {formatTime(group.startTime)} - {formatTime(group.endTime)}
                                    </span>
                                </div>
                                <p className="text-sm text-text-primary leading-relaxed">
                                    {group.texts.map((text, i) => (
                                        <span key={i}>
                                            {highlightText(text, searchQuery)}
                                            {i < group.texts.length - 1 && " "}
                                        </span>
                                    ))}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            {groupedData.length === 0 && (
                <div className="flex items-center justify-center py-16 text-text-secondary">
                    No matching segments found
                </div>
            )}
        </ScrollArea>
    );
}
