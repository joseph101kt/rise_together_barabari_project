import { useNavigate } from "react-router-dom";
import { Clock } from "lucide-react";
import { Button } from "./ui/button";

// Palette for cards without a `color` field — cycles through brand shades
const CARD_COLORS = [
  "#2F3192",
  "#4b4eb8",
  "#1b1d6b",
  "#3a3da8",
  "#23257a",
];

const PathCard = ({ path, index = 0, status }) => {
  const navigate = useNavigate();

  // Extract skills directly from the backend API response
  const skillNames = path.skills || [];

  const handleViewPath = () => {
    navigate(`/learning-paths/${path.id}`);
  };

  const cardColor = path.color || CARD_COLORS[index % CARD_COLORS.length];

  return (
    <article
      className="group relative flex flex-col overflow-hidden rounded-2xl border border-border transition-all hover:-translate-y-0.5 cursor-pointer"
      style={{ boxShadow: "var(--shadow-soft)" }}
      onClick={handleViewPath}
    >
      {/* Color band */}
      <div
        className="relative h-28 w-full overflow-hidden"
        style={{
          background: `linear-gradient(135deg, ${cardColor} 0%, #1b1d6b 120%)`,
        }}
      >
        <div
          className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full blur-2xl"
          style={{
            background: "radial-gradient(circle, #FFD230 0%, transparent 70%)",
            opacity: 0.45,
          }}
        />
        {/* Status badge */}
        {status && (
          <div className="absolute top-3 left-4 z-10">
            <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-white shadow-sm ${
              status === "completed" 
                ? "bg-green-600 border border-green-500/20" 
                : "bg-amber-500 border border-amber-400/20"
            }`}>
              {status === "completed" ? "Completed" : "In Progress"}
            </span>
          </div>
        )}
        {/* Duration badge */}
        {path.estimated_completion_time && (
          <div className="absolute bottom-3 left-4 flex items-center gap-2">
            <span className="flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-white backdrop-blur">
              <Clock className="h-3 w-3" />
              {path.estimated_completion_time}
            </span>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-4 p-5">
        <div className="space-y-2">
          <h3 className="font-display text-lg font-semibold leading-tight text-foreground">
            {path.title}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {path.description}
          </p>
        </div>

        {/* Skills / tags from mock data */}
        {skillNames.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {skillNames.slice(0, 3).map((skill) => (
              <span
                key={skill.id}
                className="rounded-md bg-secondary px-2 py-0.5 text-[11px] font-medium text-secondary-foreground"
              >
                {skill.name}
              </span>
            ))}
            {skillNames.length > 3 && (
              <span className="rounded-md px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                +{skillNames.length - 3}
              </span>
            )}
          </div>
        )}

        <div className="mt-auto pt-2">
          <Button
            size="sm"
            className="w-full rounded-lg font-semibold text-white"
            style={{ background: "var(--gradient-button)" }}
            onClick={(e) => { e.stopPropagation(); handleViewPath(); }}
          >
            View Path
          </Button>
        </div>
      </div>
    </article>
  );
};

export default PathCard;