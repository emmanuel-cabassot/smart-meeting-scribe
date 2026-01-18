import type { Group } from "./group";

// Meeting Types
export type MeetingStatus = "pending" | "processing" | "completed" | "failed";

export interface Meeting {
    id: number;
    title: string;
    status: MeetingStatus;
    s3_path: string | null;
    task_id: string | null;
    created_at: string;
    updated_at: string;
    owner_id: number;
    transcription_result: TranscriptionResult | null;
    groups: Group[];
}

export interface TranscriptionSegment {
    speaker: string;
    start: number;
    end: number;
    text: string;
}

export interface TranscriptionResult {
    segments: TranscriptionSegment[];
    text?: string;
    language?: string;
    duration?: number;
}

export interface MeetingCreate {
    title?: string;
    group_ids: number[];
}

export interface MeetingUpdate {
    title?: string;
}
