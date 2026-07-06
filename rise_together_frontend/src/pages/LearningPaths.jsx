import { useMemo, useState, useEffect } from "react";
import { Search } from "lucide-react";
import AppShell from "../components/AppShell";
import PathCard from "../components/PathCard";
import { Input } from "../components/ui/input";
import API from "../lib/api";
import Loader from "../components/ui/Loader";


const LearningPaths = () => {
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all"); // "all" or "yours"
  const [allPaths, setAllPaths] = useState([]);
  const [userPaths, setUserPaths] = useState([]);
  const [hasFetchedUserPaths, setHasFetchedUserPaths] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch only the global modules catalog on initial mount
  useEffect(() => {
    const fetchModules = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await API.get("/modules");
        setAllPaths(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load learning paths.");
      } finally {
        setLoading(false);
      }
    };

    fetchModules();
  }, []);

  // Fetch user's enrolled modules only when switching to "Your Paths"
  useEffect(() => {
    if (activeTab === "yours" && !hasFetchedUserPaths) {
      const fetchUserPaths = async () => {
        try {
          const response = await API.get("/user_modules");
          setUserPaths(response.data);
          setHasFetchedUserPaths(true);
        } catch (err) {
          setError(err.response?.data?.detail || "Failed to load your learning paths.");
        }
      };
      fetchUserPaths();
    }
  }, [activeTab, hasFetchedUserPaths]);

  // Map user module progress status to their module IDs
  const userModuleStatusMap = useMemo(() => {
    const map = {};
    userPaths.forEach((um) => {
      map[um.module_id] = um.status;
    });
    return map;
  }, [userPaths]);

  // Derive user's active/completed learning paths
  const yourPaths = useMemo(() => {
    return allPaths.filter((path) => path.id in userModuleStatusMap);
  }, [allPaths, userModuleStatusMap]);

  // Search filter matching title and associated skill names/slugs
  const filteredPaths = useMemo(() => {
    const search = query.toLowerCase().trim();
    const sourceList = activeTab === "all" ? allPaths : yourPaths;

    if (!search) return sourceList;

    return sourceList.filter((path) => {
      const matchesTitle = path.title.toLowerCase().includes(search);
      const matchesSkills = path.skills?.some(
        (skill) =>
          skill.name.toLowerCase().includes(search) ||
          skill.slug.toLowerCase().includes(search)
      );
      return matchesTitle || matchesSkills;
    });
  }, [query, activeTab, allPaths, yourPaths]);

  return (
    <AppShell>
      <div className="bg-slate-50/50 min-h-screen">
        {/* Hero Section */}
        <section
          className="relative overflow-hidden border-b border-border/50"
          style={{
            background: "linear-gradient(160deg, #e2d9ff 0%, #d4c9ff 35%, #fff3cf 100%)"
          }}
        >
          {/* Background glow effects */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
            <div className="absolute top-1/2 left-1/4 h-[300px] w-[300px] rounded-full bg-[#6366f1]/15 blur-[80px]" />
            <div className="absolute top-1/2 right-1/4 h-[300px] w-[300px] rounded-full bg-[#facc15]/15 blur-[80px]" />
          </div>

          <div className="relative mx-auto max-w-6xl px-6 py-16 text-foreground z-10">
            <div className="h-1 w-12 rounded-full" style={{ background: "var(--brand-indigo)" }} />
            <h1 className="mt-4 font-display text-4xl font-semibold leading-tight sm:text-5xl text-foreground">
              Learning paths built around{" "}
              <br className="hidden sm:block" />
              <span className="font-bold" style={{ color: "var(--brand-indigo)" }}>real outcomes</span>.
            </h1>
            <p className="mt-4 max-w-2xl text-base text-muted-foreground">
              Hand-picked, time-boxed paths combining the best free resources with
              a study group of 5–6 peers and written feedback from working
              professionals.
            </p>

            {/* Search */}
            <div className="mt-8 max-w-xl">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search paths, skills, or topics…"
                  className="h-12 rounded-xl border-transparent bg-white pl-10 text-foreground shadow-lg"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Tab Controls */}
        <section className="mx-auto max-w-6xl px-6 pt-8">
          <div className="flex border-b border-border/60">
            <button
              onClick={() => setActiveTab("all")}
              className={`border-b-2 px-6 py-3 text-sm font-semibold transition-all ${
                activeTab === "all"
                  ? "border-[color:var(--brand-indigo)] text-[color:var(--brand-indigo)]"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              All Paths
            </button>
            <button
              onClick={() => setActiveTab("yours")}
              className={`border-b-2 px-6 py-3 text-sm font-semibold transition-all ${
                activeTab === "yours"
                  ? "border-[color:var(--brand-indigo)] text-[color:var(--brand-indigo)]"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Your Paths
            </button>
          </div>
        </section>

        {/* Loading & Error States */}
        {loading ? (
          <Loader />
        ) : error ? (
          <div className="mx-auto max-w-6xl px-6 py-12">
            <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-center text-red-500">
              {error}
            </div>
          </div>
        ) : (
          <>
            {/* Count */}
            <section className="mx-auto max-w-6xl px-6 pt-6">
              <p className="text-sm text-muted-foreground">
                Showing{" "}
                <span className="font-semibold text-foreground">{filteredPaths.length}</span>{" "}
                of {activeTab === "all" ? allPaths.length : yourPaths.length} paths
              </p>
            </section>

            {/* Cards Grid */}
            <section className="mx-auto max-w-6xl px-6 py-8 pb-20">
              {filteredPaths.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-border p-12 text-center text-muted-foreground">
                  No paths found. Try a different search query or select another tab.
                </div>
              ) : (
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {filteredPaths.map((path, idx) => (
                    <PathCard 
                      key={path.id} 
                      path={path} 
                      index={idx} 
                      status={userModuleStatusMap[path.id]}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
};

export default LearningPaths;