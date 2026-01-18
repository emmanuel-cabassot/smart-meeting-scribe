"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/toaster";
import type { User, AuthTokens, LoginCredentials, UserCreate } from "@/types";

export function useAuth() {
    const router = useRouter();
    const { token, user, isAuthenticated, isLoading, login: storeLogin, logout: storeLogout, setUser } = useAuthStore();

    /**
     * Login with email and password
     */
    const login = useCallback(
        async (credentials: LoginCredentials) => {
            try {
                // FastAPI OAuth2 expects form-data with "username" and "password"
                const formData = new FormData();
                formData.append("username", credentials.username);
                formData.append("password", credentials.password);

                const tokens = await api.postForm<AuthTokens>("/auth/login", formData);

                // Fetch user profile
                // Note: Need to set token first for the /users/me call
                useAuthStore.getState().setToken(tokens.access_token);
                const userProfile = await api.get<User>("/users/me");

                // Update store
                storeLogin(tokens.access_token, userProfile);

                toast.success("Connexion réussie", `Bienvenue, ${userProfile.full_name || userProfile.email} !`);

                // Redirect to dashboard
                router.push("/");

                return { success: true };
            } catch (error) {
                const message = error instanceof Error ? error.message : "Erreur de connexion";
                toast.error("Erreur de connexion", message);
                return { success: false, error: message };
            }
        },
        [router, storeLogin]
    );

    /**
     * Register a new account
     */
    const register = useCallback(
        async (data: UserCreate) => {
            try {
                await api.post<User>("/auth/register", data);

                toast.success("Compte créé", "Vous pouvez maintenant vous connecter.");

                // Redirect to login
                router.push("/login");

                return { success: true };
            } catch (error) {
                const message = error instanceof Error ? error.message : "Erreur lors de l'inscription";
                toast.error("Erreur d'inscription", message);
                return { success: false, error: message };
            }
        },
        [router]
    );

    /**
     * Logout and redirect to login
     */
    const logout = useCallback(() => {
        storeLogout();
        toast.success("Déconnexion", "À bientôt !");
        router.push("/login");
    }, [router, storeLogout]);

    /**
     * Refresh user profile from API
     */
    const refreshUser = useCallback(async () => {
        if (!token) return;

        try {
            const userProfile = await api.get<User>("/users/me");
            setUser(userProfile);
        } catch {
            // If refresh fails, logout
            storeLogout();
        }
    }, [token, setUser, storeLogout]);

    return {
        // State
        token,
        user,
        isAuthenticated,
        isLoading,

        // Actions
        login,
        register,
        logout,
        refreshUser,
    };
}
