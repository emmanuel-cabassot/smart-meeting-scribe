# 🎯 Prompts v0.app - Smart Meeting Scribe

> Prompts optimisés pour générer des composants avec v0.app

---

## 1. Smart Card Meeting

```
Create a "SmartCard" React component for a meeting transcription app using shadcn/ui.

## Context
This is for a dark-themed meeting transcription app (style: Linear.app / YouTube Studio).

## Data Structure (TypeScript)
The card receives a Meeting object:

type MeetingStatus = "pending" | "processing" | "completed" | "failed";

interface Meeting {
  id: number;
  title: string;
  status: MeetingStatus;
  created_at: string; // ISO date
  transcription_result: {
    segments: Array<{ speaker: string; start: number; end: number; text: string }>;
    duration?: number; // in seconds
  } | null;
  groups: Array<{ id: number; name: string; type: "department" | "project" | "recurring" }>;
}

## Card Anatomy
1. **Header**: Title + relative date ("2 hours ago")
2. **Badges row**: Group badges (colored by type) + Status badge
3. **AI Summary section** (only if status = completed): Glassmorphism encart with 2-3 bullet points preview
4. **Audio player** (only if status = completed): Simple HTML5 audio with custom styled progress bar
5. **Actions row**: 
   - "Read Transcript" button → navigates to /meetings/{id}
   - "Chat" button (disabled for MVP)
   - "..." dropdown menu (Edit title, Download, Delete)

## Status States
- `pending`: Show spinner + "Transcribing..."
- `processing`: Show progress bar with percentage
- `completed`: Show AI summary + audio player
- `failed`: Show red error badge + "Retry" button

## Styling Requirements
- Dark theme (bg: #141416, text: #FAFAFA)
- Glassmorphism effect for AI summary (rgba(255,255,255,0.03), backdrop-blur)
- Accent color: #8B5CF6 (violet)
- Border: rgba(255,255,255,0.08)
- Hover: subtle glow effect

## shadcn/ui Components to use
- Card, CardHeader, CardContent, CardFooter
- Badge (for status and groups)
- Button (for actions)
- DropdownMenu (for [...] menu)
- Progress (for processing state)
- Skeleton (for loading)

## Props

interface SmartCardProps {
  meeting: Meeting;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

## Additional Notes
- Use lucide-react icons (Play, Pause, MoreHorizontal, FileText, MessageSquare, Trash2, Pencil)
- formatRelativeDate() for "2 hours ago" display
- formatDuration() for audio duration "45:23"
- The card should be responsive and full-width on mobile
```

---

## 2. Dashboard Page (à venir)

*Prompt à ajouter après la Smart Card*

---

## 3. Meeting Detail Page (à venir)

*Prompt à ajouter après le Dashboard*

---

## 📝 Instructions d'utilisation

1. Copie le prompt de la section voulue
2. Colle-le dans [v0.app](https://v0.dev)
3. Affine si nécessaire selon le résultat
4. Exporte le code généré
5. Adapte les imports shadcn/ui aux chemins locaux (`@/components/ui/...`)

---

*Dernière mise à jour : 18 Janvier 2026*
