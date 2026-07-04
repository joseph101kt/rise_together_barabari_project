import React from "react";
import { CheckCircle2, AlertCircle, ExternalLink } from "lucide-react";
import { Button } from "./ui/button";

const ResourceCard = ({
  resource,
  enrolled = false,
  submittedLinks = [],
  onToggleLink,
  onOpenSubmitModal,
}) => {
  // Find if this link slot has a tracking record
  const submission = submittedLinks?.find(
    (sl) => sl.module_link_id === resource.module_link_id
  );
  const isCompleted = !!submission?.completed;

  // Determine fallback graphic gradient if og_image is missing
  const fallbackGradient = `linear-gradient(135deg, ${
    resource.link_type === "submission" ? "#FFD230" : "#2F3192"
  } -30%, #1b1d6b 120%)`;

  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-sm transition-all hover:shadow-md">
      {/* Visual Header */}
      {resource.og_image ? (
        <img
          src={resource.og_image}
          alt={resource.title}
          className="h-44 w-full object-cover"
        />
      ) : (
        <div
          className="h-44 w-full flex flex-col justify-end p-5 text-white"
          style={{ background: fallbackGradient }}
        >
          <span className="text-[10px] font-bold uppercase tracking-wider bg-white/10 px-2 py-0.5 rounded-full w-max backdrop-blur-sm mb-2">
            {resource.link_type}
          </span>
          <h4 className="font-display font-bold leading-tight line-clamp-2">
            {resource.title}
          </h4>
        </div>
      )}

      {/* Content Area */}
      <div className="flex flex-1 flex-col justify-between p-5 gap-4">
        <div className="space-y-1.5">
          <h3 className="font-sans text-base font-semibold leading-snug text-foreground line-clamp-1">
            {resource.title}
          </h3>
          {resource.description && (
            <p className="text-xs text-muted-foreground line-clamp-2">
              {resource.description}
            </p>
          )}
        </div>

        {/* Conditional interaction controls based on Enrollment */}
        <div className="border-t border-border/60 pt-4 mt-auto">
          {enrolled ? (
            resource.link_type === "submission" ? (
              // Assignment Submission Layout
              <div className="space-y-3">
                {submission ? (
                  <div className="rounded-xl bg-secondary/40 border border-border p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-muted-foreground uppercase">
                        Your Submission
                      </span>
                      <span className="flex items-center gap-1 text-[10px] font-bold uppercase">
                        {isCompleted ? (
                          <span className="text-green-600 flex items-center gap-0.5">
                            <CheckCircle2 className="h-3.5 w-3.5" /> Approved
                          </span>
                        ) : (
                          <span className="text-amber-500 flex items-center gap-0.5">
                            <AlertCircle className="h-3.5 w-3.5" /> Pending Review
                          </span>
                        )}
                      </span>
                    </div>
                    <a
                      href={submission.link_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1 text-xs font-semibold text-[color:var(--brand-indigo)] hover:underline truncate"
                    >
                      <ExternalLink className="h-3 w-3 shrink-0" />
                      {submission.link_title || "Submitted URL"}
                    </a>
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground italic">
                    Requires url submission to complete this path.
                  </p>
                )}

                {!submission && (
                  <Button
                    onClick={() => onOpenSubmitModal(resource)}
                    size="sm"
                    className="w-full rounded-xl font-semibold bg-[color:var(--brand-indigo)] text-white hover:opacity-95"
                  >
                    Submit Assignment
                  </Button>
                )}
              </div>
            ) : (
              // Standard Resource Checklist Layout
              <div className="flex items-center justify-between gap-4">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={isCompleted}
                    onChange={() => onToggleLink(resource, isCompleted)}
                    className="h-4.5 w-4.5 rounded border-border text-[color:var(--brand-indigo)] focus:ring-[color:var(--brand-indigo)] cursor-pointer"
                  />
                  <span className="text-xs font-semibold text-foreground">
                    {isCompleted ? "Completed" : "Mark done"}
                  </span>
                </label>

                {resource.url && (
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs font-bold text-[color:var(--brand-indigo)] hover:underline flex items-center gap-0.5"
                  >
                    Open <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            )
          ) : (
            // Viewer mode (Unenrolled)
            resource.url && (
              <a
                href={resource.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex w-full items-center justify-center rounded-xl bg-secondary px-4 py-2 text-xs font-bold text-foreground transition-all hover:bg-border/60 gap-1"
              >
                Open Resource <ExternalLink className="h-3 w-3" />
              </a>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default ResourceCard;