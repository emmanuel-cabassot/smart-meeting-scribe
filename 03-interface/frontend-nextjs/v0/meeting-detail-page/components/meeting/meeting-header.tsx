"use client";

import { Clock, FileText, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { formatDuration, type Transcript } from "@/lib/transcript-data";

interface MeetingHeaderProps {
  transcript: Transcript;
}

export function MeetingHeader({ transcript }: MeetingHeaderProps) {
  const formattedDate = new Date(transcript.date).toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const formattedTime = new Date(transcript.date).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });

  return (
    <div className="px-4 py-6 sm:px-6 border-b border-border">
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <h1 className="text-xl sm:text-2xl font-semibold text-foreground tracking-tight text-balance">
            {transcript.title}
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
            <span>{formatDuration(transcript.duration)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
