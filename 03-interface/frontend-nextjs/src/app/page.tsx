"use client";

import { useState } from "react";
import VideoUpload from "@/components/VideoUpload";
import TranscriptionViewer from "@/components/TranscriptionViewer";
import { usePolling } from "@/hooks/use-polling";
import { Loader2, Sparkles, RefreshCw } from "lucide-react";

interface UploadResponse {
  status: string;
  meeting_id: string;
  task_id: string;
  s3_path: string;
  message: string;
}

export default function Home() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const { data, isPolling, error, startPolling, stopPolling } = usePolling();

  // Déclenché quand l'upload est terminé
  const handleUploadComplete = (response: UploadResponse) => {
    if (response && response.task_id) {
      console.log("Upload réussi, ID tâche:", response.task_id);
      setTaskId(response.task_id);
      startPolling(response.task_id);
    }
  };

  const resetAll = () => {
    stopPolling();
    setTaskId(null);
  };

  return (
    <main className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-5xl mx-auto">
        {/* En-tête */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center p-3 bg-white rounded-xl shadow-sm mb-4">
            <Sparkles className="text-indigo-600 mr-2" />
            <span className="font-bold text-slate-800">
              Smart Meeting Scribe V5
            </span>
          </div>
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-2">
            Transformez vos réunions en{" "}
            <span className="text-indigo-600">Texte</span>
          </h1>
          <p className="text-slate-500">
            Transcription automatique + Identification des locuteurs
          </p>
        </div>

        {/* ÉTAT 1 : UPLOAD */}
        {!taskId && !data && (
          <div className="animate-in fade-in zoom-in-95 duration-500">
            <VideoUpload onUploadSuccess={handleUploadComplete} />
          </div>
        )}

        {/* ÉTAT 2 : TRAITEMENT (Polling) */}
        {isPolling && (
          <div className="max-w-xl mx-auto text-center py-20 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="relative inline-block">
              <Loader2 className="h-16 w-16 text-indigo-600 animate-spin" />
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mt-6">
              Analyse en cours...
            </h2>
            <p className="text-slate-500 mt-2 px-8">
              Le Worker GPU traite votre fichier (Whisper Turbo + Pyannote).
              <br />
              Cela peut prendre quelques minutes.
            </p>
            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-slate-400">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>Connecté au serveur</span>
            </div>
          </div>
        )}

        {/* ÉTAT 3 : RÉSULTAT */}
        {data && (
          <div>
            <TranscriptionViewer data={data} />
            <div className="text-center mt-8">
              <button
                onClick={resetAll}
                className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-indigo-600 transition-colors"
              >
                <RefreshCw size={16} />
                Analyser une autre réunion
              </button>
            </div>
          </div>
        )}

        {/* ÉTAT ERREUR */}
        {error && !isPolling && (
          <div className="max-w-xl mx-auto mt-8 p-6 bg-red-50 text-red-700 rounded-xl border border-red-200 text-center shadow-sm">
            <p className="font-bold text-lg mb-2">Une erreur est survenue</p>
            <p className="text-sm mb-6">{error}</p>
            <button
              onClick={resetAll}
              className="bg-white border border-red-200 text-red-600 px-4 py-2 rounded-lg font-medium hover:bg-red-50 transition-colors"
            >
              Réessayer
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
