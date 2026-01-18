"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

// Map routes to labels
const routeLabels: Record<string, string> = {
    "/": "My Feed",
    "/upload": "Upload",
    "/favorites": "Favoris",
    "/settings": "Paramètres",
    "/meetings": "Meetings",
};

export function Breadcrumb() {
    const pathname = usePathname();

    // Build breadcrumb segments
    const segments = pathname.split("/").filter(Boolean);

    // Build breadcrumb items
    const items: { label: string; href: string }[] = [
        { label: "Home", href: "/" },
    ];

    let currentPath = "";
    for (const segment of segments) {
        currentPath += `/${segment}`;
        const label = routeLabels[currentPath] || segment.charAt(0).toUpperCase() + segment.slice(1);
        items.push({ label, href: currentPath });
    }

    // If we're on the home page, just show "Home > My Feed"
    if (pathname === "/") {
        return (
            <nav className="flex items-center gap-1.5 text-sm">
                <Home className="h-4 w-4 text-text-tertiary" />
                <ChevronRight className="h-3 w-3 text-text-tertiary" />
                <span className="text-text-primary font-medium">My Feed</span>
            </nav>
        );
    }

    return (
        <nav className="flex items-center gap-1.5 text-sm">
            {items.map((item, index) => {
                const isLast = index === items.length - 1;

                return (
                    <div key={item.href} className="flex items-center gap-1.5">
                        {index === 0 ? (
                            <Link
                                href={item.href}
                                className="text-text-tertiary hover:text-text-primary transition-colors"
                            >
                                <Home className="h-4 w-4" />
                            </Link>
                        ) : (
                            <>
                                <ChevronRight className="h-3 w-3 text-text-tertiary" />
                                {isLast ? (
                                    <span className="text-text-primary font-medium">
                                        {item.label}
                                    </span>
                                ) : (
                                    <Link
                                        href={item.href}
                                        className="text-text-tertiary hover:text-text-primary transition-colors"
                                    >
                                        {item.label}
                                    </Link>
                                )}
                            </>
                        )}
                    </div>
                );
            })}
        </nav>
    );
}
