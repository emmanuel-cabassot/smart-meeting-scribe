/**
 * @file badge - Shadcn/ui Component
 * @see https://ui.shadcn.com/docs/components/badge
 * Auto-generated. Avoid direct modifications.
 */
import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
    "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2",
    {
        variants: {
            variant: {
                default:
                    "border-transparent bg-accent-primary text-white",
                secondary:
                    "border-transparent bg-bg-tertiary text-text-secondary",
                destructive:
                    "border-transparent bg-accent-error text-white",
                outline:
                    "border-border-subtle text-text-secondary bg-transparent",
                success:
                    "border-transparent bg-accent-success/20 text-accent-success",
                warning:
                    "border-transparent bg-accent-warning/20 text-accent-warning",
                processing:
                    "border-transparent bg-status-processing/20 text-status-processing",
                pending:
                    "border-transparent bg-status-pending/20 text-status-pending",
                failed:
                    "border-transparent bg-status-failed/20 text-status-failed",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
);

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, ...props }: BadgeProps) {
    return (
        <div className={cn(badgeVariants({ variant }), className)} {...props} />
    );
}

export { Badge, badgeVariants };
