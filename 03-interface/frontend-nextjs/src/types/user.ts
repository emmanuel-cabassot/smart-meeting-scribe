import { Group } from "./group";

export interface User {
    id: number;
    email: string;
    full_name: string | null;
    is_active: boolean;
    groups: Group[];
}

export interface UserCreate {
    email: string;
    password: string;
    full_name?: string;
}

export interface LoginCredentials {
    username: string; // email
    password: string;
}

export interface AuthTokens {
    access_token: string;
    token_type: string;
}
