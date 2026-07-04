import React, { useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

const Modal = ({ isOpen, onClose, title, children, className, size = "md" }) => {
  // Prevent background scrolling when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-2xl",
    "2xl": "max-w-4xl",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className={cn(
          "relative w-full rounded-2xl border border-border bg-card p-6 shadow-xl transition-all animate-in fade-in zoom-in-95 duration-200",
          sizeClasses[size] || sizeClasses.md,
          className
        )}
      >
        <div className="flex items-center justify-between border-b border-border pb-4 mb-4">
          <h3 className="font-display text-lg font-bold text-foreground">{title}</h3>
          <button 
            onClick={onClose} 
            className="rounded-lg p-1 text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto pr-1">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
