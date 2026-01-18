"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
    Mic,
    LayoutDashboard,
    Upload,
    Star,
    Building2,
    Calendar,
    FolderKanban,
    Settings,
    ChevronRight,
    User,
    LogOut
} from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { useAuth } from "@/hooks/use-auth";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarMenuSub,
    SidebarMenuSubButton,
    SidebarMenuSubItem,
    SidebarRail,
} from "@/components/ui/sidebar";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";

export function AppSidebar() {
    const pathname = usePathname();
    const { user } = useAuthStore();
    const { logout } = useAuth();

    const mainNav = [
        { label: "My Feed", href: "/", icon: LayoutDashboard, active: pathname === "/" },
        { label: "Uploads", href: "/upload", icon: Upload, active: pathname === "/upload" },
        { label: "Favorites", href: "/favorites", icon: Star, active: pathname === "/favorites" },
    ];

    // Group user's groups by type (memoized for performance)
    const userGroups = user?.groups || [];

    const groupsNav = useMemo(() => {
        const byType = {
            department: userGroups.filter((g) => g.type === "department"),
            project: userGroups.filter((g) => g.type === "project"),
            recurring: userGroups.filter((g) => g.type === "recurring"),
        };

        return [
            {
                title: "Departments",
                icon: Building2,
                items: byType.department.map((g) => ({
                    label: g.name,
                    href: `/groups/${g.id}`,
                    active: pathname === `/groups/${g.id}`,
                })),
                isActive: byType.department.length > 0,
            },
            {
                title: "Projects",
                icon: FolderKanban,
                items: byType.project.map((g) => ({
                    label: g.name,
                    href: `/groups/${g.id}`,
                    active: pathname === `/groups/${g.id}`,
                })),
                isActive: byType.project.length > 0,
            },
            {
                title: "Recurring",
                icon: Calendar,
                items: byType.recurring.map((g) => ({
                    label: g.name,
                    href: `/groups/${g.id}`,
                    active: pathname === `/groups/${g.id}`,
                })),
                isActive: byType.recurring.length > 0,
            },
        ];
    }, [userGroups, pathname]);

    return (
        <Sidebar collapsible="icon" className="border-r border-border-subtle bg-bg-secondary">
            <SidebarHeader className="px-4 py-4">
                <Link href="/" className="flex items-center gap-2 group-data-[collapsible=icon]:justify-center">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-primary/20 shrink-0">
                        <Mic className="h-5 w-5 text-accent-primary" />
                    </div>
                    <div className="group-data-[collapsible=icon]:hidden">
                        <h1 className="text-sm font-semibold text-text-primary">Smart Scribe</h1>
                        <span className="text-[10px] text-text-tertiary">v6.0</span>
                    </div>
                </Link>
            </SidebarHeader>

            <SidebarContent>
                {/* Workspace */}
                <SidebarGroup>
                    <SidebarGroupLabel className="text-[10px] uppercase tracking-wider text-text-tertiary">
                        My Workspace
                    </SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {mainNav.map((item) => (
                                <SidebarMenuItem key={item.label}>
                                    <SidebarMenuButton
                                        asChild
                                        isActive={item.active}
                                        tooltip={item.label}
                                        className={item.active ? "bg-accent-primary/10 text-accent-primary" : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"}
                                    >
                                        <Link href={item.href}>
                                            <item.icon className="h-4 w-4" />
                                            <span>{item.label}</span>
                                        </Link>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>

                {/* Groups */}
                <SidebarGroup>
                    <SidebarGroupLabel className="text-[10px] uppercase tracking-wider text-text-tertiary">
                        Groups
                    </SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {groupsNav.map((group) => (
                                <Collapsible key={group.title} defaultOpen={group.isActive} className="group/collapsible">
                                    <SidebarMenuItem>
                                        <CollapsibleTrigger asChild>
                                            <SidebarMenuButton tooltip={group.title} className="text-text-secondary hover:text-text-primary hover:bg-bg-tertiary">
                                                <group.icon className="h-4 w-4" />
                                                <span>{group.title}</span>
                                                <ChevronRight className="ml-auto h-4 w-4 transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                                            </SidebarMenuButton>
                                        </CollapsibleTrigger>
                                        <CollapsibleContent>
                                            <SidebarMenuSub>
                                                {group.items.length > 0 ? (
                                                    group.items.map((item) => (
                                                        <SidebarMenuSubItem key={item.href}>
                                                            <SidebarMenuSubButton
                                                                asChild
                                                                className={item.active
                                                                    ? "bg-accent-primary/10 text-accent-primary"
                                                                    : "text-text-secondary hover:text-text-primary"
                                                                }
                                                            >
                                                                <Link href={item.href}>
                                                                    <span>{item.label}</span>
                                                                </Link>
                                                            </SidebarMenuSubButton>
                                                        </SidebarMenuSubItem>
                                                    ))
                                                ) : (
                                                    <SidebarMenuSubItem>
                                                        <span className="px-2 py-1 text-xs text-text-tertiary italic">
                                                            No groups
                                                        </span>
                                                    </SidebarMenuSubItem>
                                                )}
                                            </SidebarMenuSub>
                                        </CollapsibleContent>
                                    </SidebarMenuItem>
                                </Collapsible>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>

            <SidebarFooter className="border-t border-border-subtle p-2">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton
                                    size="lg"
                                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground w-full"
                                >
                                    <Avatar className="h-8 w-8 rounded-lg">
                                        <AvatarFallback className="rounded-lg bg-accent-primary/20 text-accent-primary">
                                            {user?.full_name?.charAt(0) || user?.email?.charAt(0) || "U"}
                                        </AvatarFallback>
                                    </Avatar>
                                    <div className="grid flex-1 text-left text-sm leading-tight">
                                        <span className="truncate font-semibold text-text-primary">
                                            {user?.full_name || "Utilisateur"}
                                        </span>
                                        <span className="truncate text-xs text-text-tertiary">
                                            {user?.email}
                                        </span>
                                    </div>
                                    <Settings className="ml-auto size-4" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg bg-bg-secondary border-border-subtle text-text-primary"
                                side="bottom"
                                align="end"
                                sideOffset={4}
                            >
                                <DropdownMenuItem asChild className="cursor-pointer hover:bg-bg-tertiary focus:bg-bg-tertiary">
                                    <Link href="/profile">
                                        <User className="mr-2 h-4 w-4" />
                                        <span>My Profile</span>
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuItem asChild className="cursor-pointer hover:bg-bg-tertiary focus:bg-bg-tertiary">
                                    <Link href="/settings">
                                        <Settings className="mr-2 h-4 w-4" />
                                        <span>Settings</span>
                                    </Link>
                                </DropdownMenuItem>
                                <Separator className="my-1 bg-border-subtle" />
                                <DropdownMenuItem
                                    className="cursor-pointer text-accent-error hover:bg-accent-error/10 focus:bg-accent-error/10 focus:text-accent-error"
                                    onClick={logout}
                                >
                                    <LogOut className="mr-2 h-4 w-4" />
                                    <span>Logout</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
            <SidebarRail />
        </Sidebar>
    );
}
