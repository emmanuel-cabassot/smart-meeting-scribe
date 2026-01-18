import { cn } from "@/lib/utils";
import { User, FileText } from "lucide-react";

interface Segment {
    speaker: string;
    start: number;
    end: number;
    text: string;
}

interface TranscriptionViewerProps {
    data: Segment[] | null;
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function getSpeakerStyle(speakerName: string): {
    bgClass: string;
    initial: string;
} {
    const name = speakerName.toLowerCase();

    if (name.includes("femme") || name === "speaker_00") {
        return { bgClass: "bg-pink-100 text-pink-700 border-pink-200", initial: "F" };
    }
    if (name.includes("homme") || name === "speaker_01") {
        return { bgClass: "bg-blue-100 text-blue-700 border-blue-200", initial: "H" };
    }

    // Autres speakers - couleurs alternées
    const colors = [
        "bg-purple-100 text-purple-700 border-purple-200",
        "bg-green-100 text-green-700 border-green-200",
        "bg-orange-100 text-orange-700 border-orange-200",
        "bg-teal-100 text-teal-700 border-teal-200",
    ];
    const index = speakerName.charCodeAt(speakerName.length - 1) % colors.length;
    return { bgClass: colors[index], initial: speakerName.charAt(0).toUpperCase() };
}

export default function TranscriptionViewer({ data }: TranscriptionViewerProps) {
    if (!data) return null;

    // Gestion robuste : fusion.json est un array direct
    const segments: Segment[] = Array.isArray(data) ? data : [];

    return (
        <div className="w-full max-w-4xl mx-auto mt-8 bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
            {/* En-tête du rapport */}
            <div className="bg-slate-50 p-4 border-b border-slate-200 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <FileText className="text-indigo-600" size={20} />
                    <h3 className="font-bold text-slate-800">Compte-rendu IA</h3>
                </div>
                <span className="text-xs font-semibold bg-green-100 text-green-700 px-3 py-1 rounded-full border border-green-200">
                    Terminé
                </span>
            </div>

            {/* Contenu Scrollable */}
            <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                {segments.length === 0 ? (
                    <div className="text-center text-slate-500 py-10">
                        <p>Aucun dialogue détecté.</p>
                    </div>
                ) : (
                    segments.map((seg, idx) => {
                        const speakerName = seg.speaker || "Inconnu";
                        const { bgClass, initial } = getSpeakerStyle(speakerName);

                        return (
                            <div key={idx} className="flex gap-4 group">
                                {/* Avatar Locuteur */}
                                <div className="flex-shrink-0 pt-1">
                                    <div
                                        className={cn(
                                            "w-10 h-10 rounded-full flex items-center justify-center shadow-sm border font-bold text-xs",
                                            bgClass
                                        )}
                                    >
                                        {initial !== speakerName.charAt(0).toUpperCase() ? (
                                            initial
                                        ) : (
                                            <User size={16} />
                                        )}
                                    </div>
                                </div>

                                {/* Texte */}
                                <div className="flex-1">
                                    <div className="flex items-baseline gap-2 mb-1">
                                        <span className="font-bold text-slate-800 text-sm">
                                            {speakerName}
                                        </span>
                                        <span className="text-xs text-slate-400 font-mono">
                                            {formatTime(seg.start)} - {formatTime(seg.end)}
                                        </span>
                                    </div>
                                    <div className="text-slate-700 leading-relaxed text-base bg-slate-50 p-3 rounded-lg rounded-tl-none border border-transparent group-hover:border-slate-200 transition-colors">
                                        {seg.text}
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
