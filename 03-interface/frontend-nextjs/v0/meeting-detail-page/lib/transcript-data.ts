export interface TranscriptSegment {
  speaker: string;
  start: number;
  end: number;
  text: string;
}

export interface Transcript {
  id: number;
  title: string;
  date: string;
  duration: number;
  status: "completed" | "processing" | "draft";
  segments: TranscriptSegment[];
}

export const transcript: Transcript = {
  id: 1,
  title: "Q1 Roadmap Review",
  date: "2023-10-15T10:00:00Z",
  duration: 3600,
  status: "completed",
  segments: [
    { speaker: "Alice", start: 0, end: 15, text: "Welcome everyone to our Q1 roadmap review meeting. I hope you're all doing well today." },
    { speaker: "Alice", start: 15, end: 30, text: "Let's start by reviewing our goals for this quarter and see where we stand." },
    { speaker: "Alice", start: 30, end: 45, text: "First, I want to highlight the progress we've made on the main product features." },
    { speaker: "Bob", start: 45, end: 60, text: "Thanks Alice. I'd like to add some context about the engineering timeline." },
    { speaker: "Bob", start: 60, end: 90, text: "We've completed the authentication module ahead of schedule, which gives us more time for the dashboard features." },
    { speaker: "Bob", start: 90, end: 120, text: "The API integrations are at about 80% completion, and we expect to finish by next week." },
    { speaker: "Carol", start: 120, end: 150, text: "From the design side, we've finalized all the mockups for the mobile app. The team is ready to hand off to development." },
    { speaker: "Carol", start: 150, end: 180, text: "We also conducted user testing last week and received very positive feedback on the new navigation patterns." },
    { speaker: "Alice", start: 180, end: 210, text: "That's great to hear. Let's talk about our priorities for the remaining weeks of the quarter." },
    { speaker: "Alice", start: 210, end: 240, text: "I'd like to focus on getting the beta release ready by the end of this month." },
    { speaker: "David", start: 240, end: 270, text: "I have some concerns about the timeline. We still have several critical bugs that need to be addressed." },
    { speaker: "David", start: 270, end: 300, text: "The performance issues on the analytics page are particularly challenging and may require more time." },
    { speaker: "Bob", start: 300, end: 330, text: "I agree with David. We should prioritize stability over new features at this point." },
    { speaker: "Alice", start: 330, end: 360, text: "Good point. Let's allocate more resources to bug fixes and revisit the feature timeline." },
    { speaker: "Carol", start: 360, end: 390, text: "I can help with the analytics page redesign to improve perceived performance while engineering works on the backend." },
    { speaker: "Alice", start: 390, end: 420, text: "Perfect. Let's schedule a follow-up meeting next week to track our progress." },
    { speaker: "Alice", start: 420, end: 450, text: "Thank you all for your updates and insights. This was a productive discussion." },
  ],
};

export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

export function getSpeakerColor(speaker: string): string {
  const colors: Record<string, string> = {
    Alice: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    Bob: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    Carol: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    David: "bg-rose-500/20 text-rose-400 border-rose-500/30",
  };
  return colors[speaker] || "bg-muted text-muted-foreground border-border";
}

export function getSpeakerAvatarColor(speaker: string): string {
  const colors: Record<string, string> = {
    Alice: "bg-blue-500",
    Bob: "bg-emerald-500",
    Carol: "bg-amber-500",
    David: "bg-rose-500",
  };
  return colors[speaker] || "bg-muted";
}
