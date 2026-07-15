import React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const Loader = ({ className, fullPage = false, size = "md", ...props }) => {
  const sizeClasses = {
    sm: "h-6 w-6",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  return (
    <div
      className={cn(
        "flex w-full items-center justify-center bg-background text-[color:var(--brand-indigo)]",
        fullPage ? "min-h-screen" : "min-h-[45vh]",
        className
      )}
      {...props}
    >
      <Loader2 className={cn("animate-spin", sizeClasses[size] || sizeClasses.md)} />
    </div>
  );
};

export default Loader;
