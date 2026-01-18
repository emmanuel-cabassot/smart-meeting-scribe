"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    Mic,
    LayoutDashboard,
    Upload,
    Star,
    Building2,
    FolderKanban,
    CalendarClock,
    Settings,
    ChevronDown,
} from "lucide-react";
import { useState } from "react";

interface NavItem {
    label: string;
    href: string;
    icon: React.ReactNode;
}

interface NavGroup {
    title: string;
    items: NavItem[];
    collapsible?: boolean;
}

const mainNav: NavItem[] = [
    { label: "My Feed", href: "/", icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: "Uploads", href: "/upload", icon: <Upload className="h-4 w-4" /> },
    { label: "Favoris", href: "/favorites", icon: <Star className="h-4 w-4" /> },
];

const groupsNav: NavGroup[] = [
    {
        title: "Departments",
        collapsible: true,
        items: [
            { label: "Tous", href: "/groups/all", icon: <Building2 className="h-4 w-4" /> },
        ],
    },
    {
        title: "Projects",
        collapsible: true,
        items: [],
    },
    {
        title: "Recurring",
        collapsible: true,
        items: [],
    },
];

export function Sidebar() {
    const pathname = usePathname();
    const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
        Departments: true,
        Projects: true,
        Recurring: true,
    });

    const toggleGroup = (title: string) => {
        setExpandedGroups((prev) => ({
            ...prev,
            [title]: !prev[title],
        }));
    };

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-bg-secondary border-r border-border-subtle flex flex-col z-40">
            {/* Logo */}
            <div className="p-4 border-b border-border-subtle">
                <Link href="/" className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-accent-primary/20">
                        <Mic className="w-5 h-5 text-accent-primary" />
                    </div>
                    <div>
                        <h1 className="font-semibold text-text-primary text-sm">
                            Smart Scribe
                        </h1>
                        <span className="text-xs text-text-tertiary">V6.0</span>
                    </div>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto p-3 space-y-6">
                {/* My Workspace */}
                <div>
                    <h3 className="px-3 mb-2 text-xs font-semibold text-text-tertiary uppercase tracking-wider">
                        My Workspace
                    </h3>
                    <ul className="space-y-1">
                        {mainNav.map((item) => (
                            <li key={item.href}>
                                <Link
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                                        pathname === item.href
                                            ? "bg-accent-primary/10 text-accent-primary"
                                            : "text-text-secondary hover:bg-bg-tertiary hover:text-text-primary"
                                    )}
                                >
                                    {item.icon}
                                    {item.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Groups */}
                <div>
                    <h3 className="px-3 mb-2 text-xs font-semibold text-text-tertiary uppercase tracking-wider">
                        Groups
                    </h3>
                    <div className="space-y-2">
                        {groupsNav.map((group) => (
                            <div key={group.title}>
                                {/* Group header */}
                                <button
                                    onClick={() => toggleGroup(group.title)}
                                    className="w-full flex items-center justify-between px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary transition-colors"
                                >
                                    <span className="font-medium">{group.title}</span>
                                    <ChevronDown
                                        className={cn(
                                            "h-4 w-4 transition-transform",
                                            expandedGroups[group.title] ? "" : "-rotate-90"
                                        )}
                                    />
                                </button>

                                {/* Group items */}
                                {expandedGroups[group.title] && (
                                    <ul className="ml-3 space-y-1">
                                        {group.items.length > 0 ? (
                                            group.items.map((item) => (
                                                <li key={item.href}>
                                                    <Link
                                                        href={item.href}
                                                        className={cn(
                                                            "flex items-center gap-3 px-3 py-1.5 rounded-lg text-sm transition-colors",
                                                            pathname === item.href
                                                                ? "bg-accent-primary/10 text-accent-primary"
                                                                : "text-text-secondary hover:bg-bg-tertiary hover:text-text-primary"
                                                        )}
                                                    >
                                                        {item.icon}
                                                        {item.label}
                                                    </Link>
                                                </li>
                                            ))
                                        ) : (
                                            <li className="px-3 py-1.5 text-xs text-text-tertiary italic">
                                                Aucun groupe
                                            </li>
                                        )}
                                    </ul>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </nav>

            {/* Bottom - Settings */}
            <div className="p-3 border-t border-border-subtle">
                <Link
                    href="/settings"
                    className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                        pathname === "/settings"
                            ? "bg-accent-primary/10 text-accent-primary"
                            : "text-text-secondary hover:bg-bg-tertiary hover:text-text-primary"
                    )}
                >
                    <Settings className="h-4 w-4" />
                    Paramètres
                </Link>
            </div>
        </aside>
    );
}
