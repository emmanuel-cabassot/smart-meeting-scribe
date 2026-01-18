"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Search, Upload, Bell, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Route labels mapping
const ROUTE_LABELS: Record<string, string> = {
    "": "My Feed",
    "upload": "Upload",
    "favorites": "Favorites",
    "groups": "Groups",
    "meetings": "Meetings",
    "settings": "Settings",
};

export function TopHeader() {
    const pathname = usePathname();

    // Build breadcrumb items from pathname
    const breadcrumbItems = useMemo(() => {
        const segments = pathname.split("/").filter(Boolean);

        if (segments.length === 0) {
            return [{ label: "My Feed", href: "/", isCurrentPage: true }];
        }

        const items: { label: string; href: string; isCurrentPage: boolean }[] = [];
        let currentPath = "";

        segments.forEach((segment, index) => {
            currentPath += `/${segment}`;
            const isLast = index === segments.length - 1;

            // Get label from mapping or capitalize segment
            const label = ROUTE_LABELS[segment] ||
                (isNaN(Number(segment)) ? segment.charAt(0).toUpperCase() + segment.slice(1) : `#${segment}`);

            items.push({
                label,
                href: currentPath,
                isCurrentPage: isLast,
            });
        });

        return items;
    }, [pathname]);

    return (
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-border-subtle bg-bg-primary/80 px-4 py-3 backdrop-blur-xl">
            <TooltipProvider>
                <div className="flex items-center gap-2">
                    <SidebarTrigger className="-ml-1" />
                    <Separator orientation="vertical" className="mr-2 h-4 bg-border-subtle" />
                    <Breadcrumb>
                        <BreadcrumbList>
                            <BreadcrumbItem>
                                <BreadcrumbLink href="/" className="text-text-secondary hover:text-text-primary">
                                    Home
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            {breadcrumbItems.map((item, index) => (
                                <span key={item.href} className="contents">
                                    <BreadcrumbSeparator />
                                    <BreadcrumbItem>
                                        {item.isCurrentPage ? (
                                            <BreadcrumbPage className="text-text-primary">
                                                {item.label}
                                            </BreadcrumbPage>
                                        ) : (
                                            <BreadcrumbLink
                                                href={item.href}
                                                className="text-text-secondary hover:text-text-primary"
                                            >
                                                {item.label}
                                            </BreadcrumbLink>
                                        )}
                                    </BreadcrumbItem>
                                </span>
                            ))}
                        </BreadcrumbList>
                    </Breadcrumb>
                </div>

                <div className="relative w-full max-w-md mx-4 hidden md:block">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
                    <Input
                        type="search"
                        placeholder="Search meetings, insights, speakers... ⌘K"
                        className="w-full pl-9 pr-12 bg-bg-tertiary border-transparent focus:border-border-bright text-text-primary placeholder:text-text-tertiary"
                    />
                </div>

                <div className="flex items-center gap-3">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button variant="ghost" size="icon" className="text-text-secondary hover:bg-bg-tertiary hover:text-text-primary">
                                <Sparkles className="h-4 w-4 text-accent-primary" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Ask AI about your meetings</p>
                        </TooltipContent>
                    </Tooltip>

                    <Button variant="ghost" size="icon" className="text-text-secondary hover:bg-bg-tertiary hover:text-text-primary">
                        <Bell className="h-5 w-5" />
                    </Button>

                    <Button asChild size="sm" className="gap-2 bg-accent-primary text-white hover:bg-accent-secondary">
                        <Link href="/upload">
                            <Upload className="h-4 w-4" />
                            Upload
                        </Link>
                    </Button>
                </div>
            </TooltipProvider>
        </header>
    );
}
