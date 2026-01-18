"use client";

import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";
import Link from "next/link";
import { Upload, Mic, Clock, CheckCircle2, AlertCircle } from "lucide-react";
import { SmartCard, SmartCardSkeleton } from "@/components/features/meetings";
import { useMeetings } from "@/hooks/use-meetings";

export default function DashboardPage() {
    const { user } = useAuthStore();
    const { meetings, isLoading, error, refetch } = useMeetings();

    // Stats calculations
    const totalMeetings = meetings.length;
    const pendingMeetings = meetings.filter(m => m.status === "pending" || m.status === "processing").length;
    const completedMeetings = meetings.filter(m => m.status === "completed").length;

    // Handlers
    const handleEdit = (id: number) => {
        console.log("Edit meeting:", id);
        // TODO: Ouvrir modal d'édition
    };

    const handleDelete = (id: number) => {
        console.log("Delete meeting:", id);
        // TODO: Ouvrir modal de confirmation
    };

    const handleRetry = (id: number) => {
        console.log("Retry meeting:", id);
        // TODO: Appeler l'API pour relancer la transcription
    };

    return (
        <div className="space-y-8">
            {/* Welcome header */}
            <div>
                <h1 className="text-2xl font-bold text-text-primary">
                    Welcome{user?.full_name ? `, ${user.full_name}` : ""} 👋
                </h1>
                <p className="text-text-secondary mt-1">
                    Here's an overview of your recent transcriptions
                </p>
            </div>

            {/* Quick stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="glass-card">
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2">
                            <Mic className="h-4 w-4" />
                            Total meetings
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold text-text-primary">{totalMeetings}</p>
                    </CardContent>
                </Card>

                <Card className="glass-card">
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-status-pending" />
                            In progress
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold text-status-pending">{pendingMeetings}</p>
                    </CardContent>
                </Card>

                <Card className="glass-card">
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2">
                            <CheckCircle2 className="h-4 w-4 text-accent-success" />
                            Completed
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold text-accent-success">{completedMeetings}</p>
                    </CardContent>
                </Card>
            </div>

            {/* Meetings Feed */}
            <div>
                <div className="mb-4">
                    <h2 className="text-lg font-semibold text-text-primary">
                        Recent Meetings
                    </h2>
                </div>

                {/* Error state */}
                {error && (
                    <Card className="glass-card max-w-2xl mx-auto border-red-500/20">
                        <CardContent className="flex flex-col items-center justify-center py-8">
                            <div className="p-3 rounded-full bg-red-500/10 mb-3">
                                <AlertCircle className="h-6 w-6 text-red-400" />
                            </div>
                            <h3 className="text-base font-semibold text-text-primary mb-1">
                                Failed to load meetings
                            </h3>
                            <p className="text-text-secondary text-sm text-center mb-4">
                                {error.message}
                            </p>
                            <Button variant="outline" size="sm" onClick={refetch}>
                                Try again
                            </Button>
                        </CardContent>
                    </Card>
                )}

                {/* Loading state */}
                {isLoading && !error && (
                    <div className="grid grid-cols-1 2xl:grid-cols-2 gap-4 max-w-4xl 2xl:max-w-none mx-auto 2xl:mx-0">
                        <SmartCardSkeleton />
                        <SmartCardSkeleton />
                        <SmartCardSkeleton />
                        <SmartCardSkeleton />
                    </div>
                )}

                {/* Empty state */}
                {!isLoading && !error && meetings.length === 0 && (
                    <Card className="glass-card max-w-2xl mx-auto">
                        <CardContent className="flex flex-col items-center justify-center py-16">
                            <div className="p-4 rounded-full bg-accent-primary/10 mb-4">
                                <Mic className="h-8 w-8 text-accent-primary" />
                            </div>
                            <h3 className="text-lg font-semibold text-text-primary mb-2">
                                No meetings yet
                            </h3>
                            <p className="text-text-secondary text-center max-w-md mb-6">
                                Upload your first audio or video file to start transcribing
                                your meetings with automatic speaker identification.
                            </p>
                            <Button asChild size="lg">
                                <Link href="/upload">
                                    <Upload className="h-4 w-4 mr-2" />
                                    Upload your first meeting
                                </Link>
                            </Button>
                        </CardContent>
                    </Card>
                )}

                {/* Meetings list - Responsive grid */}
                {/* Desktop large (2xl: >1536px): 2 colonnes */}
                {/* Desktop/Tablette: 1 colonne centrée max-width 800px */}
                {!isLoading && !error && meetings.length > 0 && (
                    <div className="grid grid-cols-1 2xl:grid-cols-2 gap-4 max-w-4xl 2xl:max-w-none mx-auto 2xl:mx-0">
                        {meetings.map((meeting) => (
                            <SmartCard
                                key={meeting.id}
                                meeting={meeting}
                                progress={meeting.status === "processing" ? 65 : 0}
                                onEdit={handleEdit}
                                onDelete={handleDelete}
                                onRetry={handleRetry}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
