"use client";

import { useAuth } from "@/hooks/use-auth";
import { getInitials } from "@/lib/utils";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Settings, LogOut, User } from "lucide-react";
import Link from "next/link";

export function UserDropdown() {
    const { user, logout } = useAuth();

    const initials = user ? getInitials(user.full_name, user.email) : "??";
    const displayName = user?.full_name || user?.email || "Utilisateur";

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-bg-tertiary transition-colors outline-none">
                    {/* Avatar */}
                    <div className="w-8 h-8 rounded-full bg-accent-primary/20 flex items-center justify-center">
                        <span className="text-sm font-medium text-accent-primary">
                            {initials}
                        </span>
                    </div>
                </button>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                        <p className="text-sm font-medium text-text-primary">
                            {displayName}
                        </p>
                        {user?.email && (
                            <p className="text-xs text-text-tertiary">{user.email}</p>
                        )}
                    </div>
                </DropdownMenuLabel>

                <DropdownMenuSeparator />

                <DropdownMenuItem asChild>
                    <Link href="/settings" className="cursor-pointer">
                        <Settings className="mr-2 h-4 w-4" />
                        Paramètres
                    </Link>
                </DropdownMenuItem>

                <DropdownMenuSeparator />

                <DropdownMenuItem
                    onClick={logout}
                    className="text-accent-error focus:text-accent-error cursor-pointer"
                >
                    <LogOut className="mr-2 h-4 w-4" />
                    Déconnexion
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
