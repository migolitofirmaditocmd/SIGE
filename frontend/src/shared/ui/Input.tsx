import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-semibold text-[#0B1320]">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={twMerge(
            clsx(
              "w-full h-11 px-3.5 bg-white text-[#0B1320] text-sm squircle border transition-colors",
              "border-[#64748B] focus:border-[#0A3D91] focus:ring-2 focus:ring-[#0A3D91]/20 focus:outline-none",
              "disabled:bg-[#F1F5F9] disabled:text-[#64748B] disabled:cursor-not-allowed",
              error ? "border-[#A31515] focus:border-[#A31515] focus:ring-[#A31515]/20" : "",
              className
            )
          )}
          {...props}
        />
        {error && <span className="text-xs font-medium text-[#A31515]">{error}</span>}
        {!error && helperText && <span className="text-xs text-[#334155]">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";
