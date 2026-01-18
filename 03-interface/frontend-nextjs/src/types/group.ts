// Group Types
export type GroupType = "department" | "project" | "recurring";

export interface Group {
    id: number;
    name: string;
    type: GroupType;
    description?: string;
    created_at: string;
    updated_at: string;
}

export interface GroupCreate {
    name: string;
    type: GroupType;
    description?: string;
}

export interface GroupUpdate {
    name?: string;
    type?: GroupType;
    description?: string;
}

// Group type display helpers
export const groupTypeLabels: Record<GroupType, string> = {
    department: "Département",
    project: "Projet",
    recurring: "Récurrent",
};

export const groupTypeIcons: Record<GroupType, string> = {
    department: "🏢",
    project: "📁",
    recurring: "📅",
};
