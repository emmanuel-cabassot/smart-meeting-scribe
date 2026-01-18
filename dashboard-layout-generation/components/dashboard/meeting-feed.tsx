"use client"

import { useState } from "react"
import { MeetingCard } from "./meeting-card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const filters = ["All", "Pending", "Completed"]

const meetings = [
  {
    id: 1,
    title: "Q4 Product Roadmap Review",
    date: "Today, 2:30 PM",
    duration: "45 min",
    participants: ["Alice M.", "Bob K.", "Charlie D.", "Diana L."],
    status: "completed" as const,
    insights: 12,
    actionItems: 5,
    tags: ["Product", "Strategy"],
  },
  {
    id: 2,
    title: "Marketing Campaign Sync",
    date: "Today, 11:00 AM",
    duration: "30 min",
    participants: ["Emma S.", "Frank R."],
    status: "pending" as const,
    insights: 0,
    actionItems: 0,
    tags: ["Marketing"],
  },
  {
    id: 3,
    title: "Engineering Sprint Planning",
    date: "Yesterday, 4:00 PM",
    duration: "1h 15min",
    participants: ["George T.", "Hannah W.", "Ivan P.", "Julia N.", "Kevin O."],
    status: "completed" as const,
    insights: 24,
    actionItems: 8,
    tags: ["Engineering", "Sprint"],
  },
  {
    id: 4,
    title: "Customer Success Weekly",
    date: "Yesterday, 10:00 AM",
    duration: "55 min",
    participants: ["Laura B.", "Mike C.", "Nancy D."],
    status: "completed" as const,
    insights: 18,
    actionItems: 6,
    tags: ["Customer Success", "Weekly"],
  },
]

export function MeetingFeed() {
  const [activeFilter, setActiveFilter] = useState("All")

  const filteredMeetings = meetings.filter((meeting) => {
    if (activeFilter === "All") return true
    if (activeFilter === "Pending") return meeting.status === "pending"
    if (activeFilter === "Completed") return meeting.status === "completed"
    return true
  })

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-foreground">Recent Insights</h2>

        <div className="flex items-center gap-2">
          {filters.map((filter) => (
            <Button
              key={filter}
              variant={activeFilter === filter ? "default" : "ghost"}
              size="sm"
              onClick={() => setActiveFilter(filter)}
              className={cn(
                "rounded-full px-4",
                activeFilter === filter
                  ? "bg-primary/20 text-primary hover:bg-primary/30"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {filter}
            </Button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {filteredMeetings.map((meeting) => (
          <MeetingCard key={meeting.id} meeting={meeting} />
        ))}
      </div>
    </div>
  )
}
