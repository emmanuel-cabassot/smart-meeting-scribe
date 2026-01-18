
import { TranscriptSegment } from "@/hooks/use-transcript";

/**
 * Format timestamp in seconds to MM:SS format
 */
export function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

/**
 * Get speaker badge color based on speaker name
 */
// Colors are defined here as Tailwind utility classes.
// We use an extended palette to reduce collisions (approx 20 unique hues).
export const SPEAKER_COLORS = [
    "bg-blue-500/10 text-blue-400 border-blue-500/20",     // Index 0
    "bg-emerald-500/10 text-emerald-400 border-emerald-500/20", // Index 1
    "bg-amber-500/10 text-amber-400 border-amber-500/20",   // Index 2
    "bg-violet-500/10 text-violet-400 border-violet-500/20",  // Index 3
    "bg-pink-500/10 text-pink-400 border-pink-500/20",      // Index 4
    "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",      // Index 5
    "bg-orange-500/10 text-orange-400 border-orange-500/20", // Index 6
    "bg-red-500/10 text-red-400 border-red-500/20",         // Index 7
    "bg-lime-500/10 text-lime-400 border-lime-500/20",       // Index 8
    "bg-teal-500/10 text-teal-400 border-teal-500/20",       // Index 9
    "bg-indigo-500/10 text-indigo-400 border-indigo-500/20", // Index 10
    "bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/20", // Index 11
    "bg-sky-500/10 text-sky-400 border-sky-500/20",
    "bg-purple-500/10 text-purple-400 border-purple-500/20",
    "bg-rose-500/10 text-rose-400 border-rose-500/20",
    "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    "bg-green-500/10 text-green-400 border-green-500/20",
    "bg-slate-500/10 text-slate-400 border-slate-500/20",
    "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
    "bg-stone-500/10 text-stone-400 border-stone-500/20",
    "bg-neutral-500/10 text-neutral-400 border-neutral-500/20",
    "bg-blue-600/10 text-blue-500 border-blue-600/20",
    "bg-emerald-600/10 text-emerald-500 border-emerald-600/20",
    "bg-amber-600/10 text-amber-500 border-amber-600/20",
    "bg-violet-600/10 text-violet-500 border-violet-600/20",
    "bg-pink-600/10 text-pink-500 border-pink-600/20",
];

export const AVATAR_COLORS = [
    "bg-blue-600",
    "bg-emerald-600",
    "bg-amber-600",
    "bg-violet-600",
    "bg-pink-600",
    "bg-cyan-600",
    "bg-orange-600",
    "bg-red-600",
    "bg-lime-600",
    "bg-teal-600",
    "bg-indigo-600",
    "bg-fuchsia-600",
    "bg-sky-600",
    "bg-purple-600",
    "bg-rose-600",
    "bg-yellow-600",
    "bg-green-600",
    "bg-slate-600",
    "bg-zinc-600",
    "bg-stone-600",
    "bg-neutral-600",
    "bg-blue-700",
    "bg-emerald-700",
    "bg-amber-700",
    "bg-violet-700",
    "bg-pink-700",
];



/**
 * Normalize text for accent-insensitive search.
 * Converts to lowercase, normalizes NFD, and removes diacritics.
 */
export function normalizeText(text: string): string {
    return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}

/**
 * Creates a RegExp that matches the query accent-insensitively.
 * Useful for highlighting original text.
 */
export function createSearchRegex(query: string): RegExp {
    const escaped = query
        .replace(/[.*+?^${}()|[\]\\]/g, "\\$&") // Escape regex special chars
        .toLowerCase();

    // Map base characters to their accented forms
    const accentMap: Record<string, string> = {
        a: "[aàáâãäå]",
        e: "[eèéêë]",
        i: "[iìíîï]",
        o: "[oòóôõö]",
        u: "[uùúûü]",
        c: "[cç]",
        n: "[nñ]",
        y: "[yýÿ]"
    };

    // Replace each character in the query with its accent-insensitive pattern
    const pattern = escaped
        .split("")
        .map((char) => accentMap[char] || char)
        .join("");

    return new RegExp(`(${pattern})`, "gi");
}

/**
 * Get speaker badge color based on speaker name
 * @deprecated Use map-based assignment instead
 */
export function getSpeakerColor(speaker: string): string {
    let hash = 0;
    for (let i = 0; i < speaker.length; i++) {
        hash = speaker.charCodeAt(i) + ((hash << 5) - hash);
    }
    return SPEAKER_COLORS[Math.abs(hash) % SPEAKER_COLORS.length];
}

/**
 * Get speaker avatar color (lighter bg)
 */
export function getSpeakerAvatarColor(speaker: string): string {
    const colors = [
        "bg-blue-600",
        "bg-emerald-600",
        "bg-amber-600",
        "bg-violet-600",
        "bg-pink-600",
        "bg-cyan-600",
    ];

    let hash = 0;
    for (let i = 0; i < speaker.length; i++) {
        hash = speaker.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}
