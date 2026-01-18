import { Mic } from "lucide-react";

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-bg-primary flex flex-col items-center justify-center p-4">
            {/* Logo et titre */}
            <div className="mb-8 flex flex-col items-center">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-accent-primary/20">
                        <Mic className="w-8 h-8 text-accent-primary" />
                    </div>
                    <h1 className="text-2xl font-bold text-text-primary">
                        Smart Meeting Scribe
                    </h1>
                </div>
                <p className="text-text-tertiary text-sm">
                    Transcription automatique avec identification des locuteurs
                </p>
            </div>

            {/* Contenu (login ou register) */}
            {children}

            {/* Footer */}
            <p className="mt-8 text-text-tertiary text-xs">
                © 2026 Smart Meeting Scribe • V6.0
            </p>
        </div>
    );
}
