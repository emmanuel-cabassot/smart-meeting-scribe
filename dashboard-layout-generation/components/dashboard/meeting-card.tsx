"use client"

import { Clock, Users, Lightbulb, CheckSquare, Play, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface Meeting {
  id: number
  title: string
  date: string
  duration: string
  participants: string[]
  status: "pending" | "completed"
  insights: number
  actionItems: number
  tags: string[]
}

export function MeetingCard({ meeting }: { meeting: Meeting }) {
  const isPending = meeting.status === "pending"

  return (
    <Card className="group relative overflow-hidden border-border bg-card/50 backdrop-blur-md transition-all hover:border-border/80 hover:bg-card/70 py-0">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/[0.02] to-accent/[0.02] opacity-0 transition-opacity group-hover:opacity-100" />

      <CardContent className="relative p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="mb-3 flex items-center gap-3">
              <h3 className="text-base font-medium text-foreground">{meeting.title}</h3>
              <Badge
                variant="outline"
                className={cn(
                  "text-[10px] uppercase tracking-wide",
                  isPending
                    ? "border-amber-500/30 bg-amber-500/10 text-amber-400"
                    : "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                )}
              >
                {meeting.status}
              </Badge>
            </div>

            <div className="mb-4 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5" />
                {meeting.date} · {meeting.duration}
              </span>
              <span className="flex items-center gap-1.5">
                <Users className="h-3.5 w-3.5" />
                {meeting.participants.length} participants
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {meeting.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-6">
            {!isPending && (
              <>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="text-center cursor-default">
                        <div className="flex items-center gap-1.5 text-primary">
                          <Lightbulb className="h-4 w-4" />
                          <span className="text-lg font-semibold">{meeting.insights}</span>
                        </div>
                        <span className="text-[10px] text-muted-foreground">Insights</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{meeting.insights} AI-generated insights</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="text-center cursor-default">
                        <div className="flex items-center gap-1.5 text-emerald-400">
                          <CheckSquare className="h-4 w-4" />
                          <span className="text-lg font-semibold">{meeting.actionItems}</span>
                        </div>
                        <span className="text-[10px] text-muted-foreground">Actions</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{meeting.actionItems} action items extracted</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </>
            )}

            <div className="flex items-center gap-2">
              {isPending ? (
                <Button size="sm" className="gap-2 bg-primary/20 text-primary hover:bg-primary/30">
                  <Play className="h-4 w-4" />
                  Process
                </Button>
              ) : (
                <Button variant="outline" size="sm">
                  View Details
                </Button>
              )}

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                    <span className="sr-only">More options</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>Share</DropdownMenuItem>
                  <DropdownMenuItem>Add to favorites</DropdownMenuItem>
                  <DropdownMenuItem>Export transcript</DropdownMenuItem>
                  <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2 border-t border-border pt-4">
          <div className="flex -space-x-2">
            {meeting.participants.slice(0, 4).map((participant, i) => (
              <Tooltip key={participant}>
                <TooltipTrigger asChild>
                  <Avatar
                    className="h-7 w-7 border-2 border-card"
                    style={{ zIndex: meeting.participants.length - i }}
                  >
                    <AvatarFallback className="bg-gradient-to-br from-violet-500/80 to-indigo-600/80 text-[10px] font-medium text-white">
                      {participant
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{participant}</p>
                </TooltipContent>
              </Tooltip>
            ))}
            {meeting.participants.length > 4 && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Avatar className="h-7 w-7 border-2 border-card">
                    <AvatarFallback className="bg-muted text-[10px] text-muted-foreground">
                      +{meeting.participants.length - 4}
                    </AvatarFallback>
                  </Avatar>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{meeting.participants.slice(4).join(", ")}</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>
          <span className="text-xs text-muted-foreground">
            {meeting.participants.slice(0, 2).join(", ")}
            {meeting.participants.length > 2 && ` and ${meeting.participants.length - 2} others`}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
