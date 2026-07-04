import { useState, useEffect, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import ModuleSection from "../components/ModuleSection";
import API from "../lib/api";
import AppShell from "../components/AppShell";
import Loader from "../components/ui/Loader";
import Modal from "../components/ui/Modal";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

const PathDetails = () => {
  const { id } = useParams();
  const [pathData, setPathData] = useState(null);
  const [userProgress, setUserProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [enrolling, setEnrolling] = useState(false);

  // Assignment submission form states
  const [submitModalOpen, setSubmitModalOpen] = useState(false);
  const [activeResource, setActiveResource] = useState(null);
  const [submissionType, setSubmissionType] = useState("github");
  const [submissionUrl, setSubmissionUrl] = useState("");
  const [submissionTitle, setSubmissionTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchPathDetailsAndProgress = async () => {
      setLoading(true);
      setError("");
      try {
        const [pathRes, progressRes] = await Promise.all([
          API.get(`/modules/${id}`),
          API.get(`/user_modules/${id}`).catch((err) => {
            // Silence 404 (indicating the user is not enrolled in this path yet)
            if (err.response?.status === 404) {
              return { data: null };
            }
            throw err;
          }),
        ]);
        setPathData(pathRes.data);
        setUserProgress(progressRes.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load learning path details.");
      } finally {
        setLoading(false);
      }
    };

    fetchPathDetailsAndProgress();
  }, [id]);

  // Calculate task counts and progress
  const totalLinks = useMemo(() => {
    if (!pathData) return 0;
    let count = 0;
    pathData.children?.forEach((child) => {
      count += (child.links || []).length;
    });
    return count;
  }, [pathData]);

  const completedLinks = useMemo(() => {
    if (!userProgress || !userProgress.submitted_links) return 0;
    return userProgress.submitted_links.filter((sl) => sl.completed).length;
  }, [userProgress]);

  const progressPercent = totalLinks > 0 ? Math.round((completedLinks / totalLinks) * 100) : 0;

  const handleStartStudying = async () => {
    setEnrolling(true);
    try {
      const res = await API.post("/user_modules", {
        module_id: Number(id),
      });
      setUserProgress(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to start studying. Please try again.");
    } finally {
      setEnrolling(false);
    }
  };

  // Toggle checkboxes for resources
  const handleToggleLink = async (resource, isCurrentlyCompleted) => {
    if (!userProgress) return;
    const moduleLinkId = resource.module_link_id;

    const existing = userProgress.submitted_links?.find(
      (sl) => sl.module_link_id === moduleLinkId
    );

    try {
      if (!existing) {
        // Create link progress entry first
        await API.post(`/user_modules/${id}/links`, {
          module_link_id: moduleLinkId,
          url: resource.url || "https://completed.resource",
          title: resource.title || "Completed Resource",
        });

        // Patch completed state to true
        const patchRes = await API.patch(`/user_modules/${id}/links/${moduleLinkId}`, {
          completed: true,
        });
        setUserProgress(patchRes.data);
      } else {
        // Toggle existing record
        const patchRes = await API.patch(`/user_modules/${id}/links/${moduleLinkId}`, {
          completed: !isCurrentlyCompleted,
        });
        setUserProgress(patchRes.data);
      }
    } catch (err) {
      console.error("Failed to toggle resource link:", err);
      alert("Failed to update resource completion status.");
    }
  };

  // Open assignment submission form
  const openSubmissionModal = (resource) => {
    setActiveResource(resource);
    setSubmissionType("github");
    setSubmissionUrl("");
    setSubmissionTitle(`${resource.title} Submission`);
    setSubmitModalOpen(true);
  };

  // Submit assignment link
  const handleSubmitLink = async (e) => {
    e.preventDefault();
    if (!submissionUrl.trim() || !submissionTitle.trim()) {
      alert("Please enter both a title and URL for your submission.");
      return;
    }

    setSubmitting(true);
    try {
      // Step 1: Create tracking link (default completed=false)
      await API.post(`/user_modules/${id}/links`, {
        module_link_id: activeResource.module_link_id,
        url: submissionUrl,
        title: submissionTitle,
      });

      // Step 2: Mark it complete immediately upon submission
      const patchRes = await API.patch(`/user_modules/${id}/links/${activeResource.module_link_id}`, {
        completed: true,
      });

      setUserProgress(patchRes.data);
      setSubmitModalOpen(false);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to submit assignment link.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <Loader />
      </AppShell>
    );
  }

  if (error || !pathData) {
    return (
      <AppShell>
        <div className="mx-auto max-w-2xl px-6 py-16 text-center">
          <h2 className="text-2xl font-bold text-red-500">Error Loading Path</h2>
          <p className="mt-2 text-muted-foreground">{error || "Learning path not found."}</p>
          <Link
            to="/learning-paths"
            className="mt-6 inline-block rounded-xl bg-[color:var(--brand-indigo)] px-6 py-2.5 text-sm font-semibold text-white hover:opacity-95"
          >
            Back to Learning Paths
          </Link>
        </div>
      </AppShell>
    );
  }

  const childModules = pathData.children || [];

  return (
    <AppShell>
      <div className="min-h-screen bg-background text-foreground">
        {/* Hero */}
        <section
          className="relative overflow-hidden px-6 py-16 text-white"
          style={{ background: "var(--gradient-panel)" }}
        >
          <div
            className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full blur-3xl"
            style={{
              background: "radial-gradient(circle, #FFD230 0%, transparent 70%)",
              opacity: 0.25,
            }}
          />
          <div className="relative mx-auto max-w-6xl">
            <Link
              to="/learning-paths"
              className="text-sm font-semibold hover:underline"
              style={{ color: "var(--brand-yellow)" }}
            >
              ← Back to Learning Paths
            </Link>

            <h1 className="mt-4 font-display text-4xl font-bold tracking-tight sm:text-5xl">
              {pathData.title}
            </h1>

            <p className="mt-4 max-w-3xl text-white/85 leading-relaxed">
              {pathData.description}
            </p>

            <div className="mt-6 flex flex-wrap items-center gap-4">
              {pathData.estimated_completion_time && (
                <span 
                  className="text-sm font-semibold flex items-center gap-1.5 animate-pulse" 
                  style={{ color: "var(--brand-yellow)" }}
                >
                  ⏱️ Estimated Time: {pathData.estimated_completion_time}
                </span>
              )}

              {userProgress && (
                <span className="rounded-full bg-white/20 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-white backdrop-blur shadow-sm">
                  Status: {userProgress.status === "completed" ? "Completed" : "In Progress"}
                </span>
              )}
            </div>

            {/* Progress Bar (Enrolled Only) */}
            {userProgress && totalLinks > 0 && (
              <div className="mt-8 w-full max-w-md bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between text-xs font-bold text-white/95 mb-2">
                  <span className="uppercase tracking-wider">Path Progress</span>
                  <span>{progressPercent}% ({completedLinks}/{totalLinks} tasks)</span>
                </div>
                <div className="h-2 w-full bg-white/15 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-[color:var(--brand-yellow)] transition-all duration-500 rounded-full"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>
            )}

            {!userProgress && (
              <div className="mt-8">
                <Button
                  onClick={handleStartStudying}
                  disabled={enrolling}
                  className="h-11 rounded-xl px-8 font-semibold shadow-md transition-all hover:scale-[1.02]"
                  style={{
                    background: "var(--brand-yellow)",
                    color: "var(--brand-indigo)",
                  }}
                >
                  {enrolling ? "Enrolling..." : "Start Studying"}
                </Button>
              </div>
            )}
          </div>
        </section>

        {/* Modules list */}
        <section className="mx-auto max-w-6xl px-6 py-12">
          {childModules.length > 0 ? (
            childModules.map((module) => (
              <ModuleSection
                key={module.id}
                module={module}
                resources={module.links || []}
                enrolled={!!userProgress}
                submittedLinks={userProgress?.submitted_links || []}
                onToggleLink={handleToggleLink}
                onOpenSubmitModal={openSubmissionModal}
              />
            ))
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-12 text-center text-muted-foreground">
              No modules are currently available in this path.
            </div>
          )}
        </section>
      </div>

      {/* Assignment Submission Modal (Reusable generic modal) */}
      <Modal
        isOpen={submitModalOpen}
        onClose={() => setSubmitModalOpen(false)}
        title="Submit Assignment Link"
        size="md"
      >
        <form onSubmit={handleSubmitLink} className="space-y-4 pt-1">
          <div>
            <Label htmlFor="submissionType" className="block text-xs font-bold uppercase text-muted-foreground mb-1.5">
              Link Type
            </Label>
            <select
              id="submissionType"
              value={submissionType}
              onChange={(e) => {
                setSubmissionType(e.target.value);
                const typeName = e.target.value.charAt(0).toUpperCase() + e.target.value.slice(1);
                setSubmissionTitle(`${activeResource?.title} (${typeName} Submission)`);
              }}
              className="w-full h-11 px-3 rounded-xl border border-border bg-background text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-[color:var(--brand-indigo)]"
            >
              <option value="github">GitHub Repository</option>
              <option value="figma">Figma File</option>
              <option value="google_drive">Google Drive Link</option>
              <option value="youtube">YouTube Demo</option>
              <option value="other">Other link</option>
            </select>
          </div>

          <div>
            <Label htmlFor="submissionTitle" className="block text-xs font-bold uppercase text-muted-foreground mb-1.5">
              Submission Title
            </Label>
            <Input
              id="submissionTitle"
              type="text"
              value={submissionTitle}
              onChange={(e) => setSubmissionTitle(e.target.value)}
              placeholder="e.g. GitHub Repository Submission"
              required
              className="h-11 rounded-xl"
            />
          </div>

          <div>
            <Label htmlFor="submissionUrl" className="block text-xs font-bold uppercase text-muted-foreground mb-1.5">
              Link URL
            </Label>
            <Input
              id="submissionUrl"
              type="url"
              value={submissionUrl}
              onChange={(e) => setSubmissionUrl(e.target.value)}
              placeholder="e.g. https://github.com/username/project"
              required
              className="h-11 rounded-xl"
            />
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-border mt-6">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setSubmitModalOpen(false)}
              className="rounded-xl font-semibold"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={submitting}
              className="rounded-xl font-semibold bg-[color:var(--brand-indigo)] text-white hover:opacity-95 px-6"
            >
              {submitting ? "Submitting..." : "Submit Link"}
            </Button>
          </div>
        </form>
      </Modal>
    </AppShell>
  );
};

export default PathDetails;