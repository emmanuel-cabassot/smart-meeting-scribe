/**
 * @file skeleton - Shadcn/ui Component
 * @see https://ui.shadcn.com/docs/components/skeleton
 * Auto-generated. Avoid direct modifications.
 */
import { cn } from '@/lib/utils'

function Skeleton({ className, ...props }: React.ComponentProps<'div'>) {
    return (
        <div
            data-slot="skeleton"
            className={cn('bg-accent animate-pulse rounded-md', className)}
            {...props}
        />
    )
}

export { Skeleton }
