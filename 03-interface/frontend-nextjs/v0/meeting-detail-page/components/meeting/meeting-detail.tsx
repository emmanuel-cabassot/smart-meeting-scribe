"use client";

import { useState, useMemo, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Toolbar } from "./toolbar";
import { MeetingHeader } from "./meeting-header";
import { TranscriptView } from "./transcript-view";
import { transcript, formatTime } from "@/lib/transcript-data";

export function MeetingDetail() {
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"detailed" | "grouped">("grouped");

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
        percentage: (duration / totalDuration) * 100,
      }))
      .sort((a, b) => b.duration - a.duration);
  }, []);

  // Get filtered segments for export
  const getExportText = useCallback(() => {
    const filteredSegments = searchQuery
      ? transcript.segments.filter((s) =>
          s.text.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : transcript.segments;

    const header = `${transcript.title}\nDate: ${new Date(transcript.date).toLocaleString()}\n\n`;
    const content = filteredSegments
      .map((s) => `[${formatTime(s.start)}] ${s.speaker}: ${s.text}`)
      .join("\n");

    return header + content;
  }, [searchQuery]);

  const handleCopy = useCallback(async () => {
    const text = getExportText();
    await navigator.clipboard.writeText(text);
  }, [getExportText]);

  const handleDownload = useCallback(() => {
    const text = getExportText();
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${transcript.title.replace(/\s+/g, "_")}_transcript.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [getExportText]);

  return (
    <div className="min-h-screen bg-background">
      <Card className="max-w-4xl mx-auto my-0 sm:my-6 border-border bg-card rounded-none sm:rounded-lg overflow-hidden">
        <Toolbar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          speakerStats={speakerStats}
          onCopy={handleCopy}
          onDownload={handleDownload}
        />
        <MeetingHeader transcript={transcript} />
        <TranscriptView
          segments={transcript.segments}
          viewMode={viewMode}
          searchQuery={searchQuery}
        />
      </Card>
    </div>
  );
}
