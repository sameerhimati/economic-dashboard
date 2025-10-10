import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        blue: "border-transparent bg-blue-100 text-blue-800 dark:bg-blue-950/50 dark:text-blue-400 dark:border-blue-800/50 dark:border hover:bg-blue-200 dark:hover:bg-blue-900/50",
        green: "border-transparent bg-green-100 text-green-800 dark:bg-green-950/50 dark:text-green-400 dark:border-green-800/50 dark:border hover:bg-green-200 dark:hover:bg-green-900/50",
        purple: "border-transparent bg-purple-100 text-purple-800 dark:bg-purple-950/50 dark:text-purple-400 dark:border-purple-800/50 dark:border hover:bg-purple-200 dark:hover:bg-purple-900/50",
        orange: "border-transparent bg-orange-100 text-orange-800 dark:bg-orange-950/50 dark:text-orange-400 dark:border-orange-800/50 dark:border hover:bg-orange-200 dark:hover:bg-orange-900/50",
        pink: "border-transparent bg-pink-100 text-pink-800 dark:bg-pink-950/50 dark:text-pink-400 dark:border-pink-800/50 dark:border hover:bg-pink-200 dark:hover:bg-pink-900/50",
        yellow: "border-transparent bg-yellow-100 text-yellow-800 dark:bg-yellow-950/50 dark:text-yellow-400 dark:border-yellow-800/50 dark:border hover:bg-yellow-200 dark:hover:bg-yellow-900/50",
        indigo: "border-transparent bg-indigo-100 text-indigo-800 dark:bg-indigo-950/50 dark:text-indigo-400 dark:border-indigo-800/50 dark:border hover:bg-indigo-200 dark:hover:bg-indigo-900/50",
        gray: "border-transparent bg-gray-100 text-gray-800 dark:bg-gray-800/50 dark:text-gray-300 dark:border-gray-700/50 dark:border hover:bg-gray-200 dark:hover:bg-gray-700/50",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
