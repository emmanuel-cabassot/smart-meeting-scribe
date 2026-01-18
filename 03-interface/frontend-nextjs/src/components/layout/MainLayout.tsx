"use client";

import { Sidebar } from "./Sidebar";
import { TopHeader } from "./TopHeader";

interface MainLayoutProps {
    children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
    return (
        <div className="min-h-screen bg-bg-primary flex">
            {/* Sidebar - Fixed left */}
            <Sidebar />

            {/* Main content area */}
            <div className="flex-1 flex flex-col ml-64">
                {/* Top Header - Fixed top */}
                <TopHeader />

                {/* Content */}
                <main className="flex-1 p-6 pt-20">
                    {children}
                </main>
            </div>
        </div>
    );
}
