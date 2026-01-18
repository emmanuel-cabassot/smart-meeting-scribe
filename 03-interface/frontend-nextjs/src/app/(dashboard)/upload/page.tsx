"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { Spinner } from "@/components/common/LoadingSpinner";
import { toast } from "@/components/ui/toaster";
import { uploadWithProgress, api } from "@/lib/api";
import { formatFileSize } from "@/lib/utils";
import type { Group, GroupType } from "@/types";
import {
    ArrowLeft,
    Upload,
    CloudUpload,
    X,
    FileAudio,
    Building2,
    FolderKanban,
    Calendar,
    CheckCircle2,
} from "lucide-react";

type UploadState = "idle" | "selected" | "uploading" | "success";

const ACCEPTED_FORMATS = ".mp3,.wav,.m4a,.mp4,.webm,.ogg,.flac";
const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024; // 2GB

function getGroupIcon(type: GroupType) {
    switch (type) {
        case "department":
            return <Building2 className="h-4 w-4" />;
        case "project":
            return <FolderKanban className="h-4 w-4" />;
        case "recurring":
            return <Calendar className="h-4 w-4" />;
    }
}

export default function UploadPage() {
    const router = useRouter();
    const [uploadState, setUploadState] = useState<UploadState>("idle");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [meetingTitle, setMeetingTitle] = useState("");
    const [selectedGroupIds, setSelectedGroupIds] = useState<number[]>([]);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isDragOver, setIsDragOver] = useState(false);
    const [showGroupError, setShowGroupError] = useState(false);
    const [groups, setGroups] = useState<Group[]>([]);
    const [isLoadingGroups, setIsLoadingGroups] = useState(true);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const { user } = useAuth();

    // Load groups from user profile
    useEffect(() => {
        if (user && user.groups) {
            setGroups(user.groups);
            setIsLoadingGroups(false);
        }
    }, [user]);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileSelect(file);
        }
    }, []);

    const handleFileSelect = (file: File) => {
        if (file.size > MAX_FILE_SIZE) {
            toast.error("Fichier trop volumineux", "La taille maximale est de 2GB");
            return;
        }
        setSelectedFile(file);
        setUploadState("selected");
        setShowGroupError(false);
    };

    const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFileSelect(file);
        }
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
        setUploadState("idle");
        setShowGroupError(false);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleGroupToggle = (groupId: number) => {
        setSelectedGroupIds((prev) =>
            prev.includes(groupId)
                ? prev.filter((id) => id !== groupId)
                : [...prev, groupId]
        );
        setShowGroupError(false);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        if (selectedGroupIds.length === 0) {
            setShowGroupError(true);
            return;
        }

        setUploadState("uploading");
        setUploadProgress(0);

        try {
            const formData = new FormData();
            formData.append("file", selectedFile);
            if (meetingTitle.trim()) {
                formData.append("title", meetingTitle.trim());
            }
            formData.append("group_ids", JSON.stringify(selectedGroupIds));

            await uploadWithProgress("/process/", formData, (progress) => {
                setUploadProgress(progress);
            });

            setUploadState("success");
            toast.success("Upload réussi", "Votre meeting est en cours de traitement");

            // Redirect after 2 seconds
            setTimeout(() => {
                router.push("/");
            }, 2000);
        } catch (error) {
            console.error("Upload failed:", error);
            toast.error("Erreur d'upload", "Une erreur est survenue");
            setUploadState("selected");
            setUploadProgress(0);
        }
    };

    const handleCancel = () => {
        setUploadState("selected");
        setUploadProgress(0);
    };

    // Group by type
    const groupsByType = {
        department: groups.filter((g) => g.type === "department"),
        project: groups.filter((g) => g.type === "project"),
        recurring: groups.filter((g) => g.type === "recurring"),
    };

    const isFormValid = selectedFile && selectedGroupIds.length > 0;

    // Success state
    if (uploadState === "success") {
        return (
            <main className="min-h-screen bg-bg-primary flex items-center justify-center p-4">
                <div className="text-center space-y-4 animate-fade-in">
                    <div className="w-16 h-16 rounded-full bg-accent-success/20 flex items-center justify-center mx-auto">
                        <CheckCircle2 className="h-8 w-8 text-accent-success" />
                    </div>
                    <h2 className="text-2xl font-semibold text-text-primary">
                        Upload terminé !
                    </h2>
                    <p className="text-text-secondary">
                        Votre meeting est en cours de traitement. Redirection...
                    </p>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-bg-primary p-4 md:p-8">
            <div className="max-w-[600px] mx-auto space-y-6">
                {/* Back Button */}
                <Button variant="ghost" asChild className="text-text-secondary hover:text-text-primary -ml-2">
                    <Link href="/">
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Retour
                    </Link>
                </Button>

                {/* Page Title */}
                <h1 className="text-2xl md:text-3xl font-semibold text-text-primary">
                    Upload New Meeting
                </h1>

                {/* Drag & Drop Zone */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`
            relative rounded-xl border-2 border-dashed p-8 md:p-12 text-center cursor-pointer
            transition-all duration-300 ease-out glass-card
            ${isDragOver
                            ? "border-accent-primary bg-accent-primary/10 scale-[1.02]"
                            : "border-border-subtle hover:border-accent-primary/50 hover:bg-bg-tertiary/30"
                        }
          `}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept={ACCEPTED_FORMATS}
                        onChange={handleFileInputChange}
                        className="sr-only"
                    />

                    {!selectedFile ? (
                        <div className="space-y-4">
                            <div className="w-16 h-16 rounded-full bg-accent-primary/10 flex items-center justify-center mx-auto">
                                <CloudUpload className="h-8 w-8 text-accent-primary" />
                            </div>
                            <div>
                                <p className="text-text-primary font-medium">
                                    Glissez-déposez votre fichier audio ou vidéo ici
                                </p>
                                <p className="text-text-secondary text-sm mt-1">
                                    ou cliquez pour parcourir
                                </p>
                            </div>
                            <div className="text-xs text-text-tertiary space-y-1">
                                <p>Formats acceptés : MP3, WAV, M4A, MP4, WEBM</p>
                                <p>Taille max : 2GB</p>
                            </div>
                        </div>
                    ) : (
                        <div
                            className="flex items-center justify-between gap-4"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex items-center gap-3 min-w-0">
                                <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center flex-shrink-0">
                                    <FileAudio className="h-5 w-5 text-accent-primary" />
                                </div>
                                <div className="min-w-0 text-left">
                                    <p className="text-text-primary font-medium truncate">
                                        {selectedFile.name}
                                    </p>
                                    <p className="text-text-secondary text-sm">
                                        {formatFileSize(selectedFile.size)}
                                    </p>
                                </div>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={handleRemoveFile}
                                className="flex-shrink-0 text-text-tertiary hover:text-accent-error hover:bg-accent-error/10"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </div>

                {/* Form Fields - Only show when file is selected */}
                {selectedFile && uploadState !== "uploading" && (
                    <div className="space-y-6 animate-fade-in">
                        {/* Title Input */}
                        <div className="space-y-2">
                            <Label htmlFor="title" className="text-text-primary">
                                Titre du meeting <span className="text-text-tertiary">(optionnel)</span>
                            </Label>
                            <Input
                                id="title"
                                placeholder="Utilisera le nom du fichier si vide"
                                value={meetingTitle}
                                onChange={(e) => setMeetingTitle(e.target.value)}
                            />
                        </div>

                        {/* Group Selection */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2">
                                <Label className="text-text-primary">Sélectionner les groupes</Label>
                                <span className="text-xs px-2 py-0.5 rounded-full bg-accent-primary/20 text-accent-primary font-medium">
                                    Requis
                                </span>
                            </div>

                            {isLoadingGroups ? (
                                <div className="rounded-xl border border-border-subtle bg-bg-secondary p-6 flex items-center justify-center">
                                    <Spinner />
                                </div>
                            ) : (
                                <div className="rounded-xl border border-border-subtle bg-bg-secondary/50 p-4 space-y-4">
                                    {/* Departments */}
                                    {groupsByType.department.length > 0 && (
                                        <div className="space-y-2">
                                            <p className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
                                                Départements
                                            </p>
                                            <div className="space-y-2">
                                                {groupsByType.department.map((group) => (
                                                    <label
                                                        key={group.id}
                                                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-tertiary cursor-pointer transition-colors"
                                                    >
                                                        <Checkbox
                                                            checked={selectedGroupIds.includes(group.id)}
                                                            onCheckedChange={() => handleGroupToggle(group.id)}
                                                        />
                                                        <div className="flex items-center gap-2 text-text-primary">
                                                            {getGroupIcon(group.type)}
                                                            <span>{group.name}</span>
                                                        </div>
                                                    </label>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Projects */}
                                    {groupsByType.project.length > 0 && (
                                        <div className="space-y-2">
                                            <p className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
                                                Projets
                                            </p>
                                            <div className="space-y-2">
                                                {groupsByType.project.map((group) => (
                                                    <label
                                                        key={group.id}
                                                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-tertiary cursor-pointer transition-colors"
                                                    >
                                                        <Checkbox
                                                            checked={selectedGroupIds.includes(group.id)}
                                                            onCheckedChange={() => handleGroupToggle(group.id)}
                                                        />
                                                        <div className="flex items-center gap-2 text-text-primary">
                                                            {getGroupIcon(group.type)}
                                                            <span>{group.name}</span>
                                                        </div>
                                                    </label>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Recurring */}
                                    {groupsByType.recurring.length > 0 && (
                                        <div className="space-y-2">
                                            <p className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
                                                Récurrents
                                            </p>
                                            <div className="space-y-2">
                                                {groupsByType.recurring.map((group) => (
                                                    <label
                                                        key={group.id}
                                                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-tertiary cursor-pointer transition-colors"
                                                    >
                                                        <Checkbox
                                                            checked={selectedGroupIds.includes(group.id)}
                                                            onCheckedChange={() => handleGroupToggle(group.id)}
                                                        />
                                                        <div className="flex items-center gap-2 text-text-primary">
                                                            {getGroupIcon(group.type)}
                                                            <span>{group.name}</span>
                                                        </div>
                                                    </label>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {groups.length === 0 && (
                                        <p className="text-text-tertiary text-sm text-center py-4">
                                            Aucun groupe disponible
                                        </p>
                                    )}
                                </div>
                            )}

                            {showGroupError && (
                                <p className="text-accent-error text-sm animate-fade-in">
                                    Veuillez sélectionner au moins un groupe
                                </p>
                            )}
                        </div>
                    </div>
                )}

                {/* Upload Progress */}
                {uploadState === "uploading" && (
                    <div className="rounded-xl border border-border-subtle bg-bg-secondary/50 p-6 space-y-4 animate-fade-in">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3 min-w-0">
                                <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center flex-shrink-0">
                                    <Upload className="h-5 w-5 text-accent-primary animate-pulse" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-text-primary font-medium truncate">
                                        {selectedFile?.name}
                                    </p>
                                    <p className="text-text-secondary text-sm">
                                        Upload en cours... {Math.round(uploadProgress)}%
                                    </p>
                                </div>
                            </div>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleCancel}
                                className="text-text-tertiary hover:text-accent-error"
                            >
                                Annuler
                            </Button>
                        </div>
                        <Progress value={uploadProgress} />
                    </div>
                )}

                {/* Action Buttons */}
                {uploadState !== "uploading" && (
                    <div className="flex items-center justify-between pt-4">
                        <Button variant="ghost" asChild className="text-text-secondary">
                            <Link href="/">Annuler</Link>
                        </Button>
                        <Button onClick={handleUpload} disabled={!isFormValid}>
                            <Upload className="h-4 w-4 mr-2" />
                            Upload & Traiter
                        </Button>
                    </div>
                )}
            </div>
        </main>
    );
}
