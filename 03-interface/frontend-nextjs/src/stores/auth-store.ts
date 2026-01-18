import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";

interface AuthState {
    // State
    token: string | null;
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;

    // Actions
    setToken: (token: string) => void;
    setUser: (user: User) => void;
    login: (token: string, user: User) => void;
    logout: () => void;
    setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            // Initial state
            token: null,
            user: null,
            isAuthenticated: false,
            isLoading: true,

            // Actions
            setToken: (token) =>
                set({
                    token,
                    isAuthenticated: !!token,
                }),

            setUser: (user) =>
                set({
                    user,
                }),

            login: (token, user) =>
                set({
                    token,
                    user,
                    isAuthenticated: true,
                    isLoading: false,
                }),

            logout: () =>
                set({
                    token: null,
                    user: null,
                    isAuthenticated: false,
                    isLoading: false,
                }),

            setLoading: (isLoading) =>
                set({
                    isLoading,
                }),
        }),
        {
            name: "auth-storage", // localStorage key
            partialize: (state) => ({
                token: state.token,
                user: state.user,
                isAuthenticated: state.isAuthenticated,
            }),
            onRehydrateStorage: () => (state) => {
                // When rehydrating from localStorage, set loading to false
                state?.setLoading(false);
            },
        }
    )
);
