import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "muted" | "elevated";
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "default", children, ...props }, ref) => {
    const baseStyles = "squircle-lg border border-[#CBD5E1] p-5 sm:p-6 transition-all";

    const variantStyles = {
      default: "bg-white shadow-sm",
      muted: "bg-[#F8FAFC]",
      elevated: "bg-white shadow-md hover:shadow-lg",
    };

    return (
      <div
        ref={ref}
        className={twMerge(clsx(baseStyles, variantStyles[variant], className))}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";
