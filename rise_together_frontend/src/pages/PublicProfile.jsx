import React, { useState, useEffect, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import { 
  Briefcase, 
  GraduationCap, 
  Link2, 
  User, 
  Calendar, 
  ArrowLeft,
  Mail,
  Edit3,
  Trash2,
  PlusCircle,
  ExternalLink
} from "lucide-react";
import API from "../lib/api";
import AppShell from "../components/AppShell";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import Loader from "../components/ui/Loader";
import Modal from "../components/ui/Modal";
import { useAuth } from "../context/AuthContext";
import { userService } from "../services/userService";

const PublicProfile = () => {
  const { id } = useParams();
  const { currentUser } = useAuth();
  
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Edit Modal States
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("general");
  const [saving, setSaving] = useState(false);

  // General Profile Form States
  const [headline, setHeadline] = useState("");
  const [bio, setBio] = useState("");

  // Lists form states
  const [formEducation, setFormEducation] = useState([]);
  const [formExperience, setFormExperience] = useState([]);
  const [formLinks, setFormLinks] = useState([]);
  
  // Skills states
  const [availableSkills, setAvailableSkills] = useState([]);
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [skillsSearch, setSkillsSearch] = useState("");

  // Add Item Temp States (to build lists)
  const [newExp, setNewExp] = useState({ company: "", role: "", start_date: "", end_date: "", description: "" });
  const [newEdu, setNewEdu] = useState({ institution: "", degree: "", field_of_study: "", start_date: "", end_date: "", description: "" });
  const [newLink, setNewLink] = useState({ title: "", url: "", link_type: "portfolio", description: "" });

  const isOwner = currentUser && currentUser.id === Number(id);

  const fetchProfile = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await API.get(`/users/${id}`);
      setProfileData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load profile details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [id]);

  // Load all available skills from DB when editing is opened
  useEffect(() => {
    if (editModalOpen) {
      const fetchSkills = async () => {
        try {
          const res = await API.get("/skills");
          setAvailableSkills(res.data);
        } catch (err) {
          console.error("Failed to load skills list:", err);
        }
      };
      fetchSkills();
    }
  }, [editModalOpen]);

  // Initialize edit forms with current profile details
  const openEditModal = () => {
    if (!profileData) return;
    setHeadline(profileData.profile.headline || "");
    setBio(profileData.profile.bio || "");
    setFormEducation(profileData.education.map(e => ({ ...e })));
    setFormExperience(profileData.experience.map(e => ({ ...e })));
    setFormLinks(profileData.profileLinks.map(l => ({ ...l })));
    setSelectedSkills(profileData.skills.map(s => ({ ...s })));
    setActiveTab("general");
    setEditModalOpen(true);
  };

  // Helper date formatter
  const formatDate = (dateStr) => {
    if (!dateStr) return "Present";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", year: "numeric" });
  };

  // Save changes handler
  const handleSaveChanges = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const cleanEducation = formEducation.map((edu) => ({
        institution: edu.institution,
        degree: edu.degree || null,
        field_of_study: edu.field_of_study || null,
        start_date: edu.start_date || null,
        end_date: edu.end_date || null,
        description: edu.description || null
      }));

      const cleanExperience = formExperience.map((exp) => ({
        company: exp.company,
        role: exp.role,
        start_date: exp.start_date || null,
        end_date: exp.end_date || null,
        description: exp.description || null
      }));

      const cleanLinks = formLinks.map((link) => ({
        title: link.title,
        url: link.url,
        link_type: link.link_type,
        description: link.description || null
      }));

      const patchPayload = {
        profile: {
          headline: headline || null,
          bio: bio || null,
        },
        education: cleanEducation,
        experience: cleanExperience,
        profileLinks: cleanLinks,
      };

      await userService.updateMyProfile(patchPayload);

      // 2. Process skills adding/removal
      const originalSkills = profileData.skills;
      const skillsToAdd = selectedSkills
        .filter((s) => !originalSkills.some((os) => os.id === s.id))
        .map((s) => s.id);
      const skillsToRemove = originalSkills
        .filter((os) => !selectedSkills.some((s) => s.id === os.id));

      if (skillsToAdd.length > 0) {
        await userService.addSkills(currentUser.id, skillsToAdd);
      }

      for (const skill of skillsToRemove) {
        await userService.removeSkill(currentUser.id, skill.id);
      }

      // Close modal and refresh profile details
      setEditModalOpen(false);
      await fetchProfile();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update profile details. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  // List builder action helpers
  const addExperienceItem = () => {
    if (!newExp.company || !newExp.role) {
      alert("Company and Role are required fields.");
      return;
    }
    setFormExperience([...formExperience, { ...newExp, id: Date.now() }]);
    setNewExp({ company: "", role: "", start_date: "", end_date: "", description: "" });
  };

  const removeExperienceItem = (id) => {
    setFormExperience(formExperience.filter((item) => item.id !== id));
  };

  const addEducationItem = () => {
    if (!newEdu.institution) {
      alert("Institution is a required field.");
      return;
    }
    setFormEducation([...formEducation, { ...newEdu, id: Date.now() }]);
    setNewEdu({ institution: "", degree: "", field_of_study: "", start_date: "", end_date: "", description: "" });
  };

  const removeEducationItem = (id) => {
    setFormEducation(formEducation.filter((item) => item.id !== id));
  };

  const addLinkItem = () => {
    if (!newLink.title || !newLink.url) {
      alert("Link Title and URL are required.");
      return;
    }
    setFormLinks([...formLinks, { ...newLink, id: Date.now() }]);
    setNewLink({ title: "", url: "", link_type: "portfolio", description: "" });
  };

  const removeLinkItem = (id) => {
    setFormLinks(formLinks.filter((item) => item.id !== id));
  };

  // Toggle skills in editor
  const handleToggleSkill = (skill) => {
    const isSelected = selectedSkills.some((s) => s.id === skill.id);
    if (isSelected) {
      setSelectedSkills(selectedSkills.filter((s) => s.id !== skill.id));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  // Filter skills based on user search query
  const filteredSkills = useMemo(() => {
    return availableSkills.filter((s) =>
      s.name.toLowerCase().includes(skillsSearch.toLowerCase())
    );
  }, [availableSkills, skillsSearch]);

  if (loading) {
    return (
      <AppShell>
        <Loader />
      </AppShell>
    );
  }

  if (error || !profileData) {
    return (
      <AppShell>
        <div className="mx-auto max-w-2xl px-6 py-16 text-center">
          <h2 className="text-2xl font-bold text-red-500">Error Loading Profile</h2>
          <p className="mt-2 text-muted-foreground">{error || "User not found"}</p>
          <Button asChild className="mt-6 font-bold text-[color:var(--brand-indigo)] bg-white border border-border hover:bg-slate-50 transition-all">
            <Link to="/learning-paths">Back to Learning Paths</Link>
          </Button>
        </div>
      </AppShell>
    );
  }

  const { user, profile, education, experience, skills, profileLinks } = profileData;

  return (
    <AppShell>
      <div 
        className="relative min-h-screen text-foreground"
        style={{
          background: "linear-gradient(160deg, #e2d9ff 0%, #d4c9ff 35%, #fff3cf 100%)"
        }}
      >
        {/* Background glow effects */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
          <div className="absolute top-1/4 left-1/4 h-[500px] w-[500px] rounded-full bg-[#6366f1]/15 blur-[100px]" />
          <div className="absolute bottom-1/4 right-1/4 h-[500px] w-[500px] rounded-full bg-[#facc15]/15 blur-[120px]" />
        </div>
      {/* 1. Header Banner Area */}
      <div className="relative h-48 w-full bg-[var(--gradient-panel)] md:h-64">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_120%,var(--brand-yellow)_0%,transparent_50%)] opacity-30 pointer-events-none" />
        <div className="mx-auto max-w-6xl px-6 pt-6 relative z-10">
          <Link 
            to="/learning-paths" 
            className="inline-flex items-center gap-2 text-sm font-semibold text-[color:var(--brand-indigo)] hover:opacity-80 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" /> Back to Learning Paths
          </Link>
        </div>
      </div>

      {/* 2. Main Profile Content */}
      <div className="mx-auto max-w-6xl px-6 pb-20">
        <div className="relative -mt-20 flex flex-col gap-8 lg:flex-row lg:items-start">
          
          {/* LEFT SIDE: Main Profile Info Cards */}
          <div className="flex-1 space-y-6">
            {/* Profile Overview Card */}
            <div className="rounded-2xl border border-border/70 bg-card p-6 shadow-[var(--shadow-soft)]">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex items-start gap-4">
                  {/* Avatar Bubble */}
                  <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl bg-[color:var(--brand-indigo)]/10 text-[color:var(--brand-indigo)] shadow-md">
                    <User className="h-12 w-12" />
                  </div>
                  <div>
                    <h1 className="font-display text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                      {user.name}
                    </h1>
                    <p className="text-md mt-1 font-semibold text-[color:var(--brand-indigo)]">
                      {profile.headline || `${user.role.charAt(0).toUpperCase() + user.role.slice(1)}`}
                    </p>
                    <p className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Calendar className="h-3.5 w-3.5" />
                      Joined {new Date(user.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })}
                    </p>
                  </div>
                </div>

                {isOwner && (
                  <Button 
                    onClick={openEditModal}
                    className="flex items-center gap-1.5 rounded-xl bg-[color:var(--brand-indigo)] text-white hover:opacity-95 text-xs font-semibold px-4 py-2 self-start"
                  >
                    <Edit3 className="h-3.5 w-3.5" /> Edit Profile
                  </Button>
                )}
              </div>

              {/* Bio Section */}
              {profile.bio && (
                <div className="mt-6 border-t border-border/50 pt-6">
                  <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-[color:var(--brand-indigo)]">
                    <User className="h-4 w-4" /> About Me
                  </h3>
                  <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-muted-foreground">
                    {profile.bio}
                  </p>
                </div>
              )}
            </div>

            {/* Experience Card */}
            <div className="rounded-2xl border border-border/70 bg-card p-6 shadow-[var(--shadow-soft)]">
              <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-[color:var(--brand-indigo)] mb-6">
                <Briefcase className="h-4 w-4" /> Experience
              </h3>
              {experience.length > 0 ? (
                <div className="relative border-l border-border/70 pl-6 space-y-8">
                  {experience.map((exp) => (
                    <div key={exp.id} className="relative group">
                      {/* Timeline dot */}
                      <span className="absolute -left-[31px] top-1.5 flex h-2.5 w-2.5 items-center justify-center rounded-full bg-[color:var(--brand-indigo)] ring-4 ring-background transition-transform group-hover:scale-125" />
                      <div>
                        <h4 className="font-display text-base font-bold text-foreground">
                          {exp.role}
                        </h4>
                        <p className="text-sm font-semibold text-muted-foreground mt-0.5">
                          {exp.company}
                        </p>
                        <p className="text-xs text-muted-foreground/80 mt-1">
                          {formatDate(exp.start_date)} – {formatDate(exp.end_date)}
                        </p>
                        {exp.description && (
                          <p className="mt-2 text-sm text-muted-foreground whitespace-pre-line">
                            {exp.description}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No experience details added yet.</p>
              )}
            </div>

            {/* Education Card */}
            <div className="rounded-2xl border border-border/70 bg-card p-6 shadow-[var(--shadow-soft)]">
              <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-[color:var(--brand-indigo)] mb-6">
                <GraduationCap className="h-4 w-4" /> Education
              </h3>
              {education.length > 0 ? (
                <div className="relative border-l border-border/70 pl-6 space-y-8">
                  {education.map((edu) => (
                    <div key={edu.id} className="relative group">
                      {/* Timeline dot */}
                      <span className="absolute -left-[31px] top-1.5 flex h-2.5 w-2.5 items-center justify-center rounded-full bg-[color:var(--brand-indigo)] ring-4 ring-background transition-transform group-hover:scale-125" />
                      <div>
                        <h4 className="font-display text-base font-bold text-foreground">
                          {edu.degree ? `${edu.degree} in ` : ""}{edu.field_of_study || "Studies"}
                        </h4>
                        <p className="text-sm font-semibold text-muted-foreground mt-0.5">
                          {edu.institution}
                        </p>
                        <p className="text-xs text-muted-foreground/80 mt-1">
                          {formatDate(edu.start_date)} – {formatDate(edu.end_date)}
                        </p>
                        {edu.description && (
                          <p className="mt-2 text-sm text-muted-foreground">
                            {edu.description}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No education details added yet.</p>
              )}
            </div>
          </div>

          {/* RIGHT SIDE: Skills and External Links Sidebar */}
          <div className="w-full space-y-6 lg:w-80 shrink-0">
            {/* Skills Card */}
            <div className="rounded-2xl border border-border/70 bg-card p-6 shadow-[var(--shadow-soft)]">
              <h3 className="text-sm font-bold uppercase tracking-wider text-[color:var(--brand-indigo)] mb-4">
                Skills
              </h3>
              {skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {skills.map((skill) => (
                    <span
                      key={skill.id}
                      className="rounded-lg bg-[color:var(--secondary)] px-3 py-1.5 text-xs font-semibold text-[color:var(--brand-indigo)]"
                    >
                      {skill.name}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No skills added yet.</p>
              )}
            </div>

            {/* Profile Links Card */}
            <div className="rounded-2xl border border-border/70 bg-card p-6 shadow-[var(--shadow-soft)]">
              <h3 className="text-sm font-bold uppercase tracking-wider text-[color:var(--brand-indigo)] mb-4">
                Links
              </h3>
              {profileLinks.length > 0 ? (
                <div className="space-y-3">
                  {profileLinks.map((link) => (
                    <a
                      key={link.id}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 rounded-xl border border-border/50 bg-background px-4 py-3 text-sm font-medium text-foreground transition-all hover:border-[color:var(--brand-indigo)] hover:text-[color:var(--brand-indigo)]"
                    >
                      <Link2 className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <div className="overflow-hidden">
                        <p className="truncate font-semibold">{link.title}</p>
                        {link.description && (
                          <p className="truncate text-xs text-muted-foreground mt-0.5">
                            {link.description}
                          </p>
                        )}
                      </div>
                    </a>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No social or project links added yet.</p>
              )}
            </div>
          </div>

        </div>
      </div>

      {/* Edit Profile Modal (Multi-tab structure) */}
      <Modal
        isOpen={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Edit Profile Details"
        size="xl"
      >
        <div className="flex flex-col md:flex-row gap-6 min-h-[50vh]">
          {/* Tab Navigation Menu */}
          <div className="flex md:flex-col border-b md:border-b-0 md:border-r border-border pb-4 md:pb-0 md:pr-4 gap-2 text-sm shrink-0">
            {["general", "skills", "experience", "education", "links"].map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`text-left px-4 py-2 rounded-lg font-semibold capitalize transition-all ${
                  activeTab === tab
                    ? "bg-[color:var(--brand-indigo)] text-white"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Form Content Panel */}
          <div className="flex-1">
            <form onSubmit={handleSaveChanges} className="space-y-6">
              
              {/* Tab 1: General (Headline, Bio) */}
              {activeTab === "general" && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="headline">Headline</Label>
                    <Input
                      id="headline"
                      type="text"
                      value={headline}
                      onChange={(e) => setHeadline(e.target.value)}
                      placeholder="e.g. Software Developer at Barabari Collective"
                      className="h-11 rounded-xl"
                    />
                  </div>
                  <div>
                    <Label htmlFor="bio">Bio</Label>
                    <textarea
                      id="bio"
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      placeholder="Write a few lines about yourself..."
                      rows={5}
                      className="w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--brand-indigo)]"
                    />
                  </div>
                </div>
              )}

              {/* Tab 2: Skills (Tags Manager) */}
              {activeTab === "skills" && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="skillsSearch">Search Skills</Label>
                    <Input
                      id="skillsSearch"
                      type="text"
                      value={skillsSearch}
                      onChange={(e) => setSkillsSearch(e.target.value)}
                      placeholder="Filter skills..."
                      className="h-11 rounded-xl"
                    />
                  </div>
                  
                  {/* Selected list */}
                  {selectedSkills.length > 0 && (
                    <div className="space-y-1.5">
                      <Label>Your Selected Skills</Label>
                      <div className="flex flex-wrap gap-1.5 p-3 rounded-xl border bg-secondary/20">
                        {selectedSkills.map((s) => (
                          <span
                            key={s.id}
                            onClick={() => handleToggleSkill(s)}
                            className="inline-flex items-center gap-1.5 cursor-pointer rounded-lg bg-[color:var(--brand-indigo)] px-2.5 py-1 text-xs font-semibold text-white hover:bg-red-500 transition-colors"
                            title="Click to remove"
                          >
                            {s.name} <span className="text-[10px] opacity-70">✕</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Available Grid */}
                  <div className="space-y-1.5">
                    <Label>Click to add skills</Label>
                    <div className="max-h-[30vh] overflow-y-auto grid grid-cols-2 sm:grid-cols-3 gap-2 border p-3 rounded-xl">
                      {filteredSkills.map((skill) => {
                        const active = selectedSkills.some((s) => s.id === skill.id);
                        return (
                          <button
                            key={skill.id}
                            type="button"
                            onClick={() => handleToggleSkill(skill)}
                            className={`px-3 py-2 text-xs font-semibold text-center border rounded-xl transition-all truncate ${
                              active
                                ? "bg-[color:var(--brand-yellow)] border-[color:var(--brand-yellow)] text-[color:var(--brand-indigo)] font-bold shadow-sm"
                                : "hover:border-[color:var(--brand-indigo)]/50"
                            }`}
                          >
                            {skill.name}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 3: Experience List */}
              {activeTab === "experience" && (
                <div className="space-y-6">
                  {/* Current experience items list */}
                  {formExperience.length > 0 && (
                    <div className="space-y-2.5">
                      <Label>Saved Experiences</Label>
                      <div className="space-y-2">
                        {formExperience.map((exp) => (
                          <div key={exp.id} className="flex items-center justify-between border bg-secondary/15 rounded-xl p-3">
                            <div className="overflow-hidden pr-2">
                              <p className="font-semibold text-sm truncate">{exp.role}</p>
                              <p className="text-xs text-muted-foreground truncate">{exp.company}</p>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeExperienceItem(exp.id)}
                              className="text-red-500 p-2 hover:bg-red-500/10 rounded-lg transition-colors shrink-0"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Add Experience sub-form */}
                  <div className="border border-dashed border-border/80 rounded-2xl p-4 bg-secondary/10 space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[color:var(--brand-indigo)] flex items-center gap-1.5">
                      <PlusCircle className="h-4 w-4" /> Add Experience Entry
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="company">Company</Label>
                        <Input
                          id="company"
                          type="text"
                          value={newExp.company}
                          onChange={(e) => setNewExp({ ...newExp, company: e.target.value })}
                          placeholder="e.g. Google"
                          className="h-10 rounded-xl"
                        />
                      </div>
                      <div>
                        <Label htmlFor="role">Role / Title</Label>
                        <Input
                          id="role"
                          type="text"
                          value={newExp.role}
                          onChange={(e) => setNewExp({ ...newExp, role: e.target.value })}
                          placeholder="e.g. Software Engineer"
                          className="h-10 rounded-xl"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="expStart">Start Date</Label>
                        <Input
                          id="expStart"
                          type="date"
                          value={newExp.start_date}
                          onChange={(e) => setNewExp({ ...newExp, start_date: e.target.value })}
                          className="h-10 rounded-xl"
                        />
                      </div>
                      <div>
                        <Label htmlFor="expEnd">End Date (Leave blank if present)</Label>
                        <Input
                          id="expEnd"
                          type="date"
                          value={newExp.end_date}
                          onChange={(e) => setNewExp({ ...newExp, end_date: e.target.value })}
                          className="h-10 rounded-xl"
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="expDesc">Description</Label>
                      <textarea
                        id="expDesc"
                        value={newExp.description}
                        onChange={(e) => setNewExp({ ...newExp, description: e.target.value })}
                        placeholder="Detail your responsibilities and achievements..."
                        rows={2}
                        className="w-full rounded-xl border border-input bg-background px-3 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--brand-indigo)]"
                      />
                    </div>
                    <Button
                      type="button"
                      onClick={addExperienceItem}
                      className="rounded-xl font-semibold bg-secondary text-foreground hover:bg-border/60 text-xs w-full py-2"
                    >
                      Add Entry to List
                    </Button>
                  </div>
                </div>
              )}

              {/* Tab 4: Education List */}
              {activeTab === "education" && (
                <div className="space-y-6">
                  {/* Current education entries list */}
                  {formEducation.length > 0 && (
                    <div className="space-y-2.5">
                      <Label>Saved Education Entries</Label>
                      <div className="space-y-2">
                        {formEducation.map((edu) => (
                          <div key={edu.id} className="flex items-center justify-between border bg-secondary/15 rounded-xl p-3">
                            <div className="overflow-hidden pr-2">
                              <p className="font-semibold text-sm truncate">{edu.degree || "Degree"} in {edu.field_of_study || "Studies"}</p>
                              <p className="text-xs text-muted-foreground truncate">{edu.institution}</p>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeEducationItem(edu.id)}
                              className="text-red-500 p-2 hover:bg-red-500/10 rounded-lg transition-colors shrink-0"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Add Education sub-form */}
                  <div className="border border-dashed border-border/80 rounded-2xl p-4 bg-secondary/10 space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[color:var(--brand-indigo)] flex items-center gap-1.5">
                      <PlusCircle className="h-4 w-4" /> Add Education Entry
                    </h4>
                    <div>
                      <Label htmlFor="institution">Institution / University</Label>
                      <Input
                        id="institution"
                        type="text"
                        value={newEdu.institution}
                        onChange={(e) => setNewEdu({ ...newEdu, institution: e.target.value })}
                        placeholder="e.g. Oxford University"
                        className="h-10 rounded-xl"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="degree">Degree / Certification</Label>
                        <Input
                          id="degree"
                          type="text"
                          value={newEdu.degree}
                          onChange={(e) => setNewEdu({ ...newEdu, degree: e.target.value })}
                          placeholder="e.g. Bachelor of Science"
                          className="h-10 rounded-xl"
                        />
                      </div>
                      <div>
                        <Label htmlFor="fieldOfStudy">Field of Study</Label>
                        <Input
                          id="fieldOfStudy"
                          type="text"
                          value={newEdu.field_of_study}
                          onChange={(e) => setNewEdu({ ...newEdu, field_of_study: e.target.value })}
                          placeholder="e.g. Computer Science"
                          className="h-10 rounded-xl"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="eduStart">Start Date</Label>
                        <Input
                          id="eduStart"
                          type="date"
                          value={newEdu.start_date}
                          onChange={(e) => setNewEdu({ ...newEdu, start_date: e.target.value })}
                          className="h-10 rounded-xl"
                        />
                      </div>
                      <div>
                        <Label htmlFor="eduEnd">End Date (Leave blank if present)</Label>
                        <Input
                          id="eduEnd"
                          type="date"
                          value={newEdu.end_date}
                          onChange={(e) => setNewEdu({ ...newEdu, end_date: e.target.value })}
                          className="h-10 rounded-xl"
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="eduDesc">Description</Label>
                      <textarea
                        id="eduDesc"
                        value={newEdu.description}
                        onChange={(e) => setNewEdu({ ...newEdu, description: e.target.value })}
                        placeholder="Mention any grades, activities or special achievements..."
                        rows={2}
                        className="w-full rounded-xl border border-input bg-background px-3 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--brand-indigo)]"
                      />
                    </div>
                    <Button
                      type="button"
                      onClick={addEducationItem}
                      className="rounded-xl font-semibold bg-secondary text-foreground hover:bg-border/60 text-xs w-full py-2"
                    >
                      Add Entry to List
                    </Button>
                  </div>
                </div>
              )}

              {/* Tab 5: Links List */}
              {activeTab === "links" && (
                <div className="space-y-6">
                  {/* Current links list */}
                  {formLinks.length > 0 && (
                    <div className="space-y-2.5">
                      <Label>Saved Profile Links</Label>
                      <div className="space-y-2">
                        {formLinks.map((link) => (
                          <div key={link.id} className="flex items-center justify-between border bg-secondary/15 rounded-xl p-3">
                            <div className="overflow-hidden pr-2">
                              <p className="font-semibold text-sm truncate">{link.title}</p>
                              <p className="text-xs text-muted-foreground truncate">{link.url} ({link.link_type})</p>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeLinkItem(link.id)}
                              className="text-red-500 p-2 hover:bg-red-500/10 rounded-lg transition-colors shrink-0"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Add Link sub-form */}
                  <div className="border border-dashed border-border/80 rounded-2xl p-4 bg-secondary/10 space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[color:var(--brand-indigo)] flex items-center gap-1.5">
                      <PlusCircle className="h-4 w-4" /> Add Profile Link
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="linkTitle">Link Title</Label>
                        <Input
                          id="linkTitle"
                          type="text"
                          value={newLink.title}
                          onChange={(e) => setNewLink({ ...newLink, title: e.target.value })}
                          placeholder="e.g. My GitHub"
                          className="h-10 rounded-xl"
                        />
                      </div>
                      <div>
                        <Label htmlFor="linkType">Link Type</Label>
                        <select
                          id="linkType"
                          value={newLink.link_type}
                          onChange={(e) => setNewLink({ ...newLink, link_type: e.target.value })}
                          className="w-full h-10 px-3 rounded-xl border border-input bg-background text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-[color:var(--brand-indigo)]"
                        >
                          <option value="github">GitHub</option>
                          <option value="portfolio">Portfolio</option>
                          <option value="projects">Projects</option>
                          <option value="resources">Resources</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="linkUrl">URL</Label>
                      <Input
                        id="linkUrl"
                        type="url"
                        value={newLink.url}
                        onChange={(e) => setNewLink({ ...newLink, url: e.target.value })}
                        placeholder="e.g. https://github.com/myusername"
                        className="h-10 rounded-xl"
                      />
                    </div>
                    <div>
                      <Label htmlFor="linkDesc">Description (Optional)</Label>
                      <Input
                        id="linkDesc"
                        type="text"
                        value={newLink.description}
                        onChange={(e) => setNewLink({ ...newLink, description: e.target.value })}
                        placeholder="Short description of where this link leads..."
                        className="h-10 rounded-xl"
                      />
                    </div>
                    <Button
                      type="button"
                      onClick={addLinkItem}
                      className="rounded-xl font-semibold bg-secondary text-foreground hover:bg-border/60 text-xs w-full py-2"
                    >
                      Add Link to List
                    </Button>
                  </div>
                </div>
              )}

              {/* Submit Buttons */}
              <div className="flex gap-3 justify-end pt-4 border-t border-border mt-8">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setEditModalOpen(false)}
                  className="rounded-xl font-semibold"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={saving}
                  className="rounded-xl font-semibold bg-[color:var(--brand-indigo)] text-white hover:opacity-95 px-6"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </div>

            </form>
          </div>
        </div>
      </Modal>
      </div>
    </AppShell>
  );
};

export default PublicProfile;
