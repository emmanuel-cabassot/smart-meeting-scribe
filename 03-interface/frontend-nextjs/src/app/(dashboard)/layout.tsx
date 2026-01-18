"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { MainLayout } from "@/components/layout/MainLayout";
import { LoadingOverlay } from "@/components/common/LoadingSpinner";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const { isAuthenticated, isLoading } = useAuthStore();

    useEffect(() => {
        // Wait for hydration from localStorage
        if (!isLoading && !isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, isLoading, router]);

    // Show loading while checking auth
    if (isLoading) {
        return <LoadingOverlay />;
    }

    // Redirect if not authenticated
    if (!isAuthenticated) {
        return <LoadingOverlay />;
    }

    return <MainLayout>{children}</MainLayout>;
}
