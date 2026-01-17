# Prompt v0.app - Smart Meeting Scribe

## Pour générer la Smart Card

```
Create a dark-themed "Smart Card" component for a meeting dashboard, inspired by Linear.app and YouTube Studio.

VISUAL STYLE:
- Ultra-dark background (#0A0A0B)
- Glassmorphism effect (backdrop-blur, semi-transparent white borders)
- Violet/Indigo accent colors (#8B5CF6)
- Subtle shadows and hover glow effects

CARD STRUCTURE:
1. Header (flex row):
   - Left: Meeting title (large, white text) "Point Hebdo R&D"
   - Right: Relative time "2h ago" (gray text)

2. Badges row:
   - Group badges: Purple pill "[V5 Launch]", Blue pill "[Tech]"
   - Status badge: Green dot + "Completed"

3. AI Insights section (glassmorphism box with violet tint):
   - Icon: ✨ "AI Summary"
   - 3 bullet points:
     * "✅ Architecture S3 validée"
     * "⚠️ Bloqueur sur le Dockerfile GPU"
     * "💡 Action: Emmanuel doit patcher avant midi"

4. Audio Player (embedded):
   - Play button icon
   - Waveform visualization (blue/red gradient)
   - Time display "45:23 / 52:10"
   - Seek bar

5. Actions footer:
   - Button: "📄 Read Transcript" (secondary style)
   - Button: "💬 Chat" (ghost style)
   - Icon button: "⋯ More"

INTERACTIONS:
- Hover: Subtle glow border (violet)
- Card is clickable to open detail view
- All buttons have hover states

TECH:
- Next.js 16 / React
- TailwindCSS
- TypeScript
- Lucide icons

Make it look premium, data-rich, and professional.
```

## Pour générer le Dashboard complet

```
Create a dark-themed dashboard layout for "Smart Meeting Scribe", a meeting transcription app.

LAYOUT (3 zones):

1. LEFT SIDEBAR (fixed, 240px):
   - Dark background (#141416)
   - Logo "Smart Scribe v6.0" at top
   - Navigation sections:
     * MY WORKSPACE (My Feed - active/highlighted, Uploads, Favorites)
     * GROUPS with expandable categories:
       - Departments (R&D, Marketing, Direction)
       - Projects (V5 Launch, Audit)
       - Recurring (COMOP, Daily)
   - Bottom: User profile "Emmanuel C." with settings icon

2. TOP HEADER (sticky):
   - Breadcrumb: "Home > My Feed"
   - Center: Search bar with ⌘K hint (glassmorphism)
   - Right: "✨ Ask AI" button + large violet "UPLOAD MEETING" CTA

3. MAIN CONTENT:
   - Title: "Recent Insights"
   - Filter pills: "All", "Pending", "Completed"
   - Scrollable feed of 3-4 meeting cards (use the Smart Card from previous prompt)

VISUAL STYLE:
- Ultra-dark theme (#0A0A0B background)
- Glassmorphism throughout
- Violet/Indigo accents (#8B5CF6)
- Subtle borders (rgba(255,255,255,0.08))
- Smooth transitions and hover states

TECH:
- Next.js 16 App Router
- TailwindCSS
- TypeScript
- Framer Motion for animations

Make it look like a premium SaaS dashboard (Linear, Notion style).
```

## Pour générer la page Upload

```
Create a dark-themed upload page for audio/video files with group selection.

LAYOUT:
- Centered card (max-width 600px) on dark background
- Title: "Upload New Meeting"

COMPONENTS:
1. File Dropzone:
   - Large dashed border area (glassmorphism)
   - Icon: 📤
   - Text: "Drag & drop audio/video here or click to browse"
   - Supported formats: MP3, WAV, MP4, M4A (small gray text)
   - Max size: 2GB

2. Title Input (optional):
   - Label: "📝 Title (optional)"
   - Text input with dark styling

3. Group Selector (required):
   - Label: "🏢 Select Groups (required)"
   - Multi-checkbox list:
     * R&D (checked)
     * V5 Launch (checked)
     * Marketing (unchecked)
     * COMOP (unchecked)
   - Custom checkboxes with violet accent

4. Footer Actions:
   - Left: "Cancel" (ghost button)
   - Right: "Upload & Process →" (large violet CTA, disabled if no file)

STATES:
- Empty state (initial)
- File dragging over (highlight border)
- File selected (show filename + size)
- Uploading (progress bar)

VISUAL STYLE:
- Dark theme (#0A0A0B)
- Glassmorphism card
- Violet accents
- Smooth animations

TECH:
- React dropzone
- TailwindCSS
- TypeScript
```

---

**Instructions d'utilisation :**
1. Copie l'un des prompts ci-dessus
2. Colle-le dans v0.app
3. Affine si nécessaire selon le résultat
4. Exporte le code généré dans ton projet Next.js
