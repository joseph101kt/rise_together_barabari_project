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
  const [allUserProgress, setAllUserProgress] = useState([]);
  const [alertDialog, setAlertDialog] = useState({
    isOpen: false,
    title: "",
    message: "",
  });

  const showAlert = (title, message) => {
    setAlertDialog({ isOpen: true, title, message });
  };
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
        const [pathRes, progressRes, allProgressRes] = await Promise.all([
          API.get(`/modules/${id}`),
          API.get(`/user_modules/${id}`).catch((err) => {
            // Silence 404 (indicating the user is not enrolled in this path yet)
            if (err.response?.status === 404) {
              return { data: null };
            }
            throw err;
          }),
          API.get("/user_modules"),
        ]);
        setPathData(pathRes.data);
        setUserProgress(progressRes.data);
        setAllUserProgress(allProgressRes.data || []);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load learning path details.");
      } finally {
        setLoading(false);
      }
    };

    fetchPathDetailsAndProgress();
  }, [id]);

  // Calculate all submitted links across all enrolled modules
  const allSubmittedLinks = useMemo(() => {
    if (!allUserProgress) return [];
    return allUserProgress.flatMap((um) => um.submitted_links || []);
  }, [allUserProgress]);

  // Collect all link IDs that belong to the child modules of the current pathway
  const currentPathLinkIds = useMemo(() => {
    if (!pathData) return new Set();
    const ids = new Set();
    pathData.children?.forEach((child) => {
      child.links?.forEach((lnk) => {
        ids.add(lnk.module_link_id);
      });
    });
    return ids;
  }, [pathData]);

  // Calculate task counts and progress specific to this pathway
  const totalLinks = useMemo(() => {
    if (!pathData) return 0;
    let count = 0;
    pathData.children?.forEach((child) => {
      count += (child.links || []).length;
    });
    return count;
  }, [pathData]);

  const completedLinks = useMemo(() => {
    return allSubmittedLinks.filter(
      (sl) => sl.completed && currentPathLinkIds.has(sl.module_link_id)
    ).length;
  }, [allSubmittedLinks, currentPathLinkIds]);

  const progressPercent = totalLinks > 0 ? Math.round((completedLinks / totalLinks) * 100) : 0;

  const handleStartStudying = async () => {
    setEnrolling(true);
    try {
      const res = await API.post("/user_modules", {
        module_id: Number(id),
      });
      setUserProgress(res.data);
      // Re-fetch all progress to keep states synced
      const refreshRes = await API.get("/user_modules");
      setAllUserProgress(refreshRes.data || []);
    } catch (err) {
      showAlert("Start Studying", err.response?.data?.detail || "Failed to start studying. Please try again.");
    } finally {
      setEnrolling(false);
    }
  };

  // Toggle checkboxes for resources
  const handleToggleLink = async (resource, isCurrentlyCompleted) => {
    if (!userProgress) return;
    const moduleLinkId = resource.module_link_id;
    const childModuleId = resource.child_module_id;

    // Check if the user is enrolled in the child module
    const isEnrolledInChild = allUserProgress.some((um) => um.module_id === childModuleId);

    try {
      if (!isEnrolledInChild) {
        // Enroll in the child module first
        const enrollRes = await API.post("/user_modules", {
          module_id: childModuleId,
        });
        setAllUserProgress((prev) => [...prev, enrollRes.data]);
      }

      const existing = allSubmittedLinks.find(
        (sl) => sl.module_link_id === moduleLinkId
      );

      if (!existing) {
        // Create link progress entry first
        await API.post(`/user_modules/${childModuleId}/links`, {
          module_link_id: moduleLinkId,
          url: resource.url || "https://completed.resource",
          title: resource.title || "Completed Resource",
        });

        // Patch completed state to true
        await API.patch(`/user_modules/${childModuleId}/links/${moduleLinkId}`, {
          completed: true,
        });
      } else {
        // Toggle existing record
        await API.patch(`/user_modules/${childModuleId}/links/${moduleLinkId}`, {
          completed: !isCurrentlyCompleted,
        });
      }

      // Re-fetch progress to update the UI
      const refreshRes = await API.get("/user_modules");
      setAllUserProgress(refreshRes.data || []);
      
      const parentProgressRes = await API.get(`/user_modules/${id}`);
      setUserProgress(parentProgressRes.data);

    } catch (err) {
      console.error("Failed to toggle resource link:", err);
      showAlert("Update Failed", "Failed to update resource completion status.");
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
      showAlert("Required Input", "Please enter both a title and URL for your submission.");
      return;
    }

    const childModuleId = activeResource.child_module_id;
    const moduleLinkId = activeResource.module_link_id;

    // Check if enrolled
    const isEnrolledInChild = allUserProgress.some((um) => um.module_id === childModuleId);

    setSubmitting(true);
    try {
      if (!isEnrolledInChild) {
        // Enroll in child module
        const enrollRes = await API.post("/user_modules", {
          module_id: childModuleId,
        });
        setAllUserProgress((prev) => [...prev, enrollRes.data]);
      }

      // Step 1: Create tracking link (default completed=false)
      await API.post(`/user_modules/${childModuleId}/links`, {
        module_link_id: moduleLinkId,
        url: submissionUrl,
        title: submissionTitle,
      });

      // Step 2: Mark it complete immediately upon submission
      await API.patch(`/user_modules/${childModuleId}/links/${moduleLinkId}`, {
        completed: true,
      });

      // Re-fetch progress to update the UI
      const refreshRes = await API.get("/user_modules");
      setAllUserProgress(refreshRes.data || []);

      const parentProgressRes = await API.get(`/user_modules/${id}`);
      setUserProgress(parentProgressRes.data);

      setSubmitModalOpen(false);
    } catch (err) {
      showAlert("Submission Failed", err.response?.data?.detail || "Failed to submit assignment link.");
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
          className="relative overflow-hidden border-b border-border/50 px-6 py-16"
          style={{
            background: "linear-gradient(160deg, #e2d9ff 0%, #d4c9ff 35%, #fff3cf 100%)"
          }}
        >
          {/* Background glow effects */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
            <div className="absolute top-1/2 left-1/4 h-[300px] w-[300px] rounded-full bg-[#6366f1]/15 blur-[80px]" />
            <div className="absolute top-1/2 right-1/4 h-[300px] w-[300px] rounded-full bg-[#facc15]/15 blur-[80px]" />
          </div>

          <div className="relative mx-auto max-w-6xl z-10 text-foreground">
            <Link
              to="/learning-paths"
              className="text-sm font-semibold transition-all hover:underline"
              style={{ color: "var(--brand-indigo)" }}
            >
              ← Back to Learning Paths
            </Link>

            <h1 className="mt-4 font-display text-4xl font-bold tracking-tight sm:text-5xl text-foreground">
              {pathData.title}
            </h1>

            <p className="mt-4 max-w-3xl text-muted-foreground leading-relaxed">
              {pathData.description}
            </p>

            <div className="mt-6 flex flex-wrap items-center gap-4">
              {pathData.estimated_completion_time && (
                <span 
                  className="text-sm font-bold flex items-center gap-1.5" 
                  style={{ color: "var(--brand-indigo)" }}
                >
                  ⏱️ Estimated Time: {pathData.estimated_completion_time}
                </span>
              )}

              {userProgress && (
                <span className="rounded-full bg-indigo-50 border border-indigo-100/80 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-indigo-700 shadow-sm">
                  Status: {userProgress.status === "completed" ? "Completed" : "In Progress"}
                </span>
              )}
            </div>

            {/* Progress Bar (Enrolled Only) */}
            {userProgress && totalLinks > 0 && (
              <div className="mt-8 w-full max-w-md bg-white/70 border border-border/80 rounded-2xl p-4 shadow-sm backdrop-blur-sm">
                <div className="flex items-center justify-between text-xs font-bold text-foreground mb-2">
                  <span className="uppercase tracking-wider">Path Progress</span>
                  <span>{progressPercent}% ({completedLinks}/{totalLinks} tasks)</span>
                </div>
                <div className="h-2 w-full bg-indigo-100/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-[color:var(--brand-indigo)] transition-all duration-500 rounded-full"
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
                  className="h-11 rounded-xl px-8 font-semibold shadow-md transition-all hover:scale-[1.02] bg-[color:var(--brand-indigo)] text-white hover:opacity-95"
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
                resources={(module.links || []).map((link) => ({ ...link, child_module_id: module.id }))}
                enrolled={!!userProgress}
                submittedLinks={allSubmittedLinks.filter((sl) => currentPathLinkIds.has(sl.module_link_id))}
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

      {/* Custom Alert Modal */}
      <Modal
        isOpen={alertDialog.isOpen}
        onClose={() => setAlertDialog((prev) => ({ ...prev, isOpen: false }))}
        title={alertDialog.title}
        size="sm"
      >
        <div className="space-y-4 pt-1">
          <p className="text-sm text-muted-foreground">{alertDialog.message}</p>
          <div className="flex justify-end">
            <Button
              onClick={() => setAlertDialog((prev) => ({ ...prev, isOpen: false }))}
              className="rounded-xl font-semibold bg-[color:var(--brand-indigo)] text-white hover:opacity-95 px-6"
            >
              OK
            </Button>
          </div>
        </div>
      </Modal>

    </AppShell>
  );
};

export default PathDetails;