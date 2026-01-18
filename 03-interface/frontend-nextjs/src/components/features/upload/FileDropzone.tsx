"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileVideo, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useXHRUpload } from "@/hooks/use-upload";

interface UploadResponse {
    status: string;
    meeting_id: string;
    task_id: string;
    s3_path: string;
    message: string;
}

interface VideoUploadProps {
    onUploadSuccess?: (response: UploadResponse) => void;
}

export default function VideoUpload({ onUploadSuccess }: VideoUploadProps) {
    const [file, setFile] = useState<File | null>(null);
    const { upload, progress, status, error, reset } = useXHRUpload();

    // URL de l'API (configurable via env, défaut: localhost:5000)
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
    const UPLOAD_URL = `${API_URL}/api/v1/process/`;

    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            if (acceptedFiles?.length > 0) {
                setFile(acceptedFiles[0]);
                reset();
            }
        },
        [reset]
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { "video/*": [], "audio/*": [] },
        maxFiles: 1,
    });

    const handleStartUpload = async () => {
        if (!file) return;
        try {
            const response = await upload({ url: UPLOAD_URL, file });

            if (onUploadSuccess && response) {
                onUploadSuccess(response as UploadResponse);
            }
        } catch (e) {
            // L'erreur est gérée visuellement via le state 'error' du hook
        }
    };

    const handleRemoveFile = (e: React.MouseEvent) => {
        e.stopPropagation();
        setFile(null);
        reset();
    };

    return (
        <div className="w-full max-w-xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-semibold mb-4 text-slate-800">
                Nouvelle Analyse
            </h2>

            {/* Zone Drag & Drop */}
            <div
                {...getRootProps()}
                className={cn(
                    "border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-all duration-200",
                    isDragActive
                        ? "border-indigo-500 bg-indigo-50 scale-[1.02]"
                        : "border-slate-300 hover:bg-slate-50",
                    status === "uploading" && "opacity-50 pointer-events-none grayscale"
                )}
            >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center gap-3">
                    <div
                        className={cn(
                            "p-4 rounded-full transition-colors",
                            isDragActive
                                ? "bg-indigo-100 text-indigo-600"
                                : "bg-slate-100 text-slate-500"
                        )}
                    >
                        <UploadCloud size={32} />
                    </div>
                    <div>
                        <p className="text-lg font-medium text-slate-700">
                            {isDragActive
                                ? "Lâchez pour uploader"
                                : "Glissez votre fichier ici"}
                        </p>
                        <p className="text-sm text-slate-400 mt-1">
                            MP4, MOV, MP3, M4A, WAV (Max 2 Go)
                        </p>
                    </div>
                </div>
            </div>

            {/* Info Fichier */}
            {file && (
                <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200 flex items-center gap-4">
                    <div className="p-2 bg-white rounded-md shadow-sm text-indigo-600">
                        <FileVideo size={24} />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 truncate">
                            {file.name}
                        </p>
                        <p className="text-xs text-slate-500">
                            {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                    </div>
                    {status === "idle" && (
                        <button
                            onClick={handleRemoveFile}
                            className="text-slate-400 hover:text-red-500 transition-colors p-1"
                        >
                            <X size={20} />
                        </button>
                    )}
                </div>
            )}

            {/* Barre de Progression */}
            {status === "uploading" && (
                <div className="mt-6 space-y-2">
                    <div className="flex justify-between text-xs font-semibold text-indigo-600 uppercase tracking-wide">
                        <span>Envoi vers S3...</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-indigo-600 transition-all duration-200 ease-linear"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Succès Upload */}
            {status === "success" && (
                <div className="mt-6 p-4 bg-green-50 text-green-700 rounded-lg text-center border border-green-200">
                    <p className="font-bold">✓ Fichier envoyé</p>
                    <p className="text-sm">Lancement du traitement IA...</p>
                </div>
            )}

            {/* Erreur */}
            {status === "error" && (
                <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-lg text-center border border-red-200">
                    <p className="font-bold">Erreur d&apos;envoi</p>
                    <p className="text-sm">{error}</p>
                </div>
            )}

            {/* Bouton Action */}
            {file && status === "idle" && (
                <button
                    onClick={handleStartUpload}
                    className="mt-6 w-full bg-slate-900 hover:bg-slate-800 text-white font-medium py-3 px-4 rounded-lg transition-all active:scale-[0.98] shadow-lg shadow-slate-200"
                >
                    Lancer l&apos;analyse
                </button>
            )}
        </div>
    );
}
