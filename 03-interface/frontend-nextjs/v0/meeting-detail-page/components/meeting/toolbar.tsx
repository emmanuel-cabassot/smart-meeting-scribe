"use client";

import { ArrowLeft, Search, Copy, Download, BarChart3, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { useState } from "react";

interface SpeakerStats {
  speaker: string;
  duration: number;
  percentage: number;
}

interface ToolbarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  viewMode: "detailed" | "grouped";
  onViewModeChange: (mode: "detailed" | "grouped") => void;
  speakerStats: SpeakerStats[];
  onCopy: () => void;
  onDownload: () => void;
}

export function Toolbar({
  searchQuery,
  onSearchChange,
  viewMode,
  onViewModeChange,
  speakerStats,
  onCopy,
  onDownload,
}: ToolbarProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <TooltipProvider>
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
        <div className="flex items-center justify-between gap-4 p-4">
          {/* Left: Back button */}
          <div className="flex items-center gap-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                  <ArrowLeft className="h-4 w-4" />
                  <span className="sr-only">Go back</span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>Go back</TooltipContent>
            </Tooltip>
          </div>

          {/* Center: Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search transcript..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="pl-9 bg-secondary border-border focus-visible:ring-accent"
              />
            </div>
          </div>

          {/* Right: View toggle and actions */}
          <div className="flex items-center gap-2">
            {/* View Toggle */}
            <Tabs value={viewMode} onValueChange={(v) => onViewModeChange(v as "detailed" | "grouped")}>
              <TabsList className="bg-secondary border border-border h-9">
                <TabsTrigger value="grouped" className="text-xs data-[state=active]:bg-muted">
                  <span className="hidden sm:inline">Grouped</span>
                  <span className="sm:hidden">G</span>
                </TabsTrigger>
                <TabsTrigger value="detailed" className="text-xs data-[state=active]:bg-muted">
                  <span className="hidden sm:inline">Detailed</span>
                  <span className="sm:hidden">D</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Actions */}
            <div className="flex items-center gap-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" onClick={handleCopy} className="text-muted-foreground hover:text-foreground">
                    {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                    <span className="sr-only">Copy transcript</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{copied ? "Copied!" : "Copy transcript"}</TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" onClick={onDownload} className="text-muted-foreground hover:text-foreground">
                    <Download className="h-4 w-4" />
                    <span className="sr-only">Download transcript</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Download as .txt</TooltipContent>
              </Tooltip>

              <Popover>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <PopoverTrigger asChild>
                      <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                        <BarChart3 className="h-4 w-4" />
                        <span className="sr-only">Speaker statistics</span>
                      </Button>
                    </PopoverTrigger>
                  </TooltipTrigger>
                  <TooltipContent>Speaker stats</TooltipContent>
                </Tooltip>
                <PopoverContent className="w-72 bg-popover border-border" align="end">
                  <div className="space-y-4">
                    <h4 className="font-medium text-sm text-foreground">Speaker Talk Time</h4>
                    <div className="space-y-3">
                      {speakerStats.map((stat) => (
                        <div key={stat.speaker} className="space-y-1.5">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-foreground">{stat.speaker}</span>
                            <span className="text-muted-foreground">{stat.percentage.toFixed(1)}%</span>
                          </div>
                          <Progress value={stat.percentage} className="h-1.5" />
                        </div>
                      ))}
                    </div>
                  </div>
                </PopoverContent>
              </Popover>
            </div>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}
