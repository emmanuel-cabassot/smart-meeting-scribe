"use client";

import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Upload, Mic, Clock, CheckCircle2 } from "lucide-react";

export default function DashboardPage() {
    const { user } = useAuthStore();

    return (
        <div className="space-y-8">
            {/* Welcome header */}
            <div>
                <h1 className="text-2xl font-bold text-text-primary">
                    Bienvenue{user?.full_name ? `, ${user.full_name}` : ""} 👋
                </h1>
                <p className="text-text-secondary mt-1">
                    Voici un aperçu de vos dernières transcriptions
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
                        <p className="text-3xl font-bold text-text-primary">0</p>
                    </CardContent>
                </Card>

                <Card className="glass-card">
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-status-pending" />
                            En cours
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold text-status-pending">0</p>
                    </CardContent>
                </Card>

                <Card className="glass-card">
                    <CardHeader className="pb-2">
                        <CardDescription className="flex items-center gap-2">
                            <CheckCircle2 className="h-4 w-4 text-accent-success" />
                            Terminés
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold text-accent-success">0</p>
                    </CardContent>
                </Card>
            </div>

            {/* Empty state */}
            <Card className="glass-card">
                <CardContent className="flex flex-col items-center justify-center py-16">
                    <div className="p-4 rounded-full bg-accent-primary/10 mb-4">
                        <Mic className="h-8 w-8 text-accent-primary" />
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">
                        Aucune réunion pour le moment
                    </h3>
                    <p className="text-text-secondary text-center max-w-md mb-6">
                        Uploadez votre premier fichier audio ou vidéo pour commencer à
                        transcrire vos réunions avec identification automatique des
                        locuteurs.
                    </p>
                    <Button asChild size="lg">
                        <Link href="/upload">
                            <Upload className="h-4 w-4" />
                            Upload your first meeting
                        </Link>
                    </Button>
                </CardContent>
            </Card>

            {/* Recent meetings section - placeholder for now */}
            <div>
                <h2 className="text-lg font-semibold text-text-primary mb-4">
                    Cette semaine
                </h2>
                <p className="text-text-tertiary text-sm">
                    Les meetings apparaîtront ici une fois uploadés.
                </p>
            </div>
        </div>
    );
}
