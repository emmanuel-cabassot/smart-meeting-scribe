import * as React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
    size?: "sm" | "md" | "lg";
}

const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8",
};

export function Spinner({ size = "md", className, ...props }: SpinnerProps) {
    return (
        <div
            role="status"
            aria-label="Loading"
            className={cn("flex items-center justify-center", className)}
            {...props}
        >
            <Loader2 className={cn("animate-spin text-accent-primary", sizeClasses[size])} />
            <span className="sr-only">Loading...</span>
        </div>
    );
}

export function LoadingOverlay() {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-bg-primary/80 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-4">
                <Spinner size="lg" />
                <p className="text-text-secondary text-sm">Chargement...</p>
            </div>
        </div>
    );
}
