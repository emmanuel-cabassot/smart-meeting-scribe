import Link from "next/link";
import { Sparkles, Upload, FileText, MessageSquare } from "lucide-react";

export default function Home() {
    return (
        <main className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8 font-sans">
            <div className="max-w-4xl mx-auto">
                {/* En-tête */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center justify-center p-3 bg-white rounded-xl shadow-sm mb-4">
                        <Sparkles className="text-indigo-600 mr-2" />
                        <span className="font-bold text-slate-800">
                            Smart Meeting Scribe V6
                        </span>
                    </div>
                    <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
                        Transformez vos réunions en{" "}
                        <span className="text-indigo-600">Insights</span>
                    </h1>
                    <p className="text-slate-500 text-lg max-w-2xl mx-auto">
                        Transcription automatique, identification des locuteurs,
                        et résumés IA de vos réunions audio et vidéo.
                    </p>
                </div>

                {/* Features */}
                <div className="grid md:grid-cols-3 gap-6 mb-16">
                    <FeatureCard
                        icon={<Upload className="h-6 w-6" />}
                        title="Upload Simple"
                        description="Glissez-déposez vos fichiers audio ou vidéo"
                    />
                    <FeatureCard
                        icon={<FileText className="h-6 w-6" />}
                        title="Transcription IA"
                        description="Whisper Turbo + identification des locuteurs"
                    />
                    <FeatureCard
                        icon={<MessageSquare className="h-6 w-6" />}
                        title="Résumés Intelligents"
                        description="Insights et points clés générés automatiquement"
                    />
                </div>

                {/* CTA */}
                <div className="text-center">
                    <Link
                        href="/upload"
                        className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-4 px-8 rounded-xl transition-all shadow-lg shadow-indigo-200 hover:shadow-indigo-300 active:scale-[0.98]"
                    >
                        <Upload size={20} />
                        Uploader une réunion
                    </Link>
                </div>
            </div>
        </main>
    );
}

function FeatureCard({
    icon,
    title,
    description,
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
}) {
    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
            <div className="p-3 bg-indigo-50 rounded-lg w-fit mb-4 text-indigo-600">
                {icon}
            </div>
            <h3 className="font-semibold text-slate-800 mb-2">{title}</h3>
            <p className="text-sm text-slate-500">{description}</p>
        </div>
    );
}
