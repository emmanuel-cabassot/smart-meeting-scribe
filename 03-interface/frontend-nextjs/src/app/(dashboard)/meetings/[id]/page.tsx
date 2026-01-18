"use client";

import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, AlertCircle, Loader2 } from "lucide-react";

import { useTranscript } from "@/hooks/use-transcript";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { MeetingDetail } from "@/components/meeting/MeetingDetail";

export default function MeetingDetailPage() {
    const params = useParams();
    const router = useRouter();

    const meetingId = params.id ? parseInt(params.id as string, 10) : null;
    const { transcript, isLoading, error } = useTranscript(meetingId);

    if (isLoading) {
        return (
            <div className="flex h-[50vh] w-full items-center justify-center">
                <Loader2 className="size-8 animate-spin text-accent-primary" />
            </div>
        );
    }

    if (error || !transcript) {
        return (
            <div className="space-y-6">
                <div>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.back()}
                        className="text-text-secondary hover:text-text-primary"
                    >
                        <ArrowLeft className="mr-2 size-4" />
                        Back to Dashboard
                    </Button>
                </div>
                <Card className="border-status-failed/20 bg-status-failed/5">
                    <CardContent className="flex flex-col items-center justify-center py-12">
                        <AlertCircle className="size-12 text-status-failed mb-4" />
                        <h2 className="text-lg font-semibold text-text-primary mb-2">
                            Failed to load transcript
                        </h2>
                        <p className="text-text-secondary text-center mb-4">
                            {error?.message || "Transcript not found"}
                        </p>
                        <Button variant="outline" onClick={() => window.location.reload()}>
                            Retry
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <MeetingDetail transcript={transcript} />
    );
}
