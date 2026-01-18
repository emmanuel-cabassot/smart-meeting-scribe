"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, Upload, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { UserDropdown } from "./UserDropdown";
import { Breadcrumb } from "./Breadcrumb";

export function TopHeader() {
    const [searchQuery, setSearchQuery] = useState("");
    const pathname = usePathname();

    return (
        <header className="fixed top-0 left-64 right-0 h-14 bg-bg-secondary/80 backdrop-blur-md border-b border-border-subtle z-30 flex items-center px-6 gap-4">
            {/* Breadcrumb */}
            <Breadcrumb />

            {/* Spacer */}
            <div className="flex-1" />

            {/* Search */}
            <div className="relative w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
                <Input
                    type="search"
                    placeholder="Rechercher... ⌘K"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 h-9 bg-bg-tertiary border-transparent focus:border-border-bright"
                />
            </div>

            {/* Notifications (placeholder) */}
            <Button variant="ghost" size="icon" className="text-text-secondary">
                <Bell className="h-5 w-5" />
            </Button>

            {/* Upload Button */}
            <Button asChild>
                <Link href="/upload">
                    <Upload className="h-4 w-4" />
                    Upload
                </Link>
            </Button>

            {/* User Dropdown */}
            <UserDropdown />
        </header>
    );
}
