import React from "react";
import { Link } from "react-router-dom";
import  Logo from "../components/Logo";
import { Button } from "../components/ui/button";
import { LogIn, ArrowRight, UserPlus } from "lucide-react";

const features = [
  {
    icon: "🗺️",
    title: "Curated Learning Paths",
    description:
      "Hand-picked, time-boxed paths built from the best free resources on the internet — no paid courses required.",
  },
  {
    icon: "👥",
    title: "Peer Study Groups",
    description:
      "Study groups of 5–6 students to keep each other accountable and learn together every week.",
  },
];

const Home = () => {
  return (
    <div
      className="relative min-h-screen overflow-x-hidden text-foreground"
      style={{
        background:
          "linear-gradient(160deg, #e4dfff 0%, #dbd5ff 45%, #fff5e0 100%)",
      }}
    >
      {/* ─── Decorative background ─── */}
      <div
        className="pointer-events-none fixed inset-0 overflow-hidden z-0"
        aria-hidden
      >
        {/* Top-left purple glow */}
        <div
          className="absolute -top-40 -left-40 h-[600px] w-[600px] rounded-full blur-[120px]"
          style={{
            background:
              "radial-gradient(circle, rgba(99,102,241,0.48) 0%, transparent 70%)",
          }}
        />

        {/* Top-right yellow glow */}
        <div
          className="absolute -top-20 right-0 h-[500px] w-[500px] rounded-full blur-[120px]"
          style={{
            background:
              "radial-gradient(circle, rgba(250,204,21,0.40) 0%, transparent 70%)",
          }}
        />

        {/* Center soft purple glow */}
        <div
          className="absolute top-1/2 left-1/2 h-[700px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-[140px]"
          style={{
            background:
              "radial-gradient(circle, rgba(129,140,248,0.30) 0%, transparent 75%)",
          }}
        />

        {/* Bottom-left yellow glow */}
        <div
          className="absolute bottom-0 -left-32 h-[400px] w-[400px] rounded-full blur-[100px]"
          style={{
            background:
              "radial-gradient(circle, rgba(250,204,21,0.38) 0%, transparent 70%)",
          }}
        />

        {/* Dot grid */}
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "radial-gradient(circle, rgba(47,49,146,0.2) 1px, transparent 1px)",
            backgroundSize: "36px 36px",
            opacity: 0.18,
          }}
        />
      </div>

      {/* ─── NAV ─── */}
      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between p-6">
        <Logo />
        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost"
              className="border border-[color:var(--brand-indigo)]/40 flex items-center gap-1.5 font-semibold">
              <LogIn className="h-4 w-4" /> Sign in
            </Button>
          </Link>
          <Link to="/register">
            <Button
              className="rounded-lg font-semibold text-white shadow-md flex items-center gap-1.5"
              style={{ background: "var(--gradient-button)" }}
            >
              Get started <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      {/* HERO  */}
      <main className="relative z-10">
        <section className="mx-auto max-w-3xl px-6 py-24 text-center">

          <h1 className="font-display text-5xl font-bold leading-tight sm:text-6xl text-foreground">
            Learn together
            <br />
            <span
              style={{
                background: "var(--gradient-button)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              Rise together
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted-foreground">
            The structure, community, and feedback that top institutions provide
            naturally — built for students at government colleges across India.
          </p>

          <div className="mt-10 flex flex-wrap justify-center gap-3">
            <Link to="/register">
              <Button
                size="lg"
                className="rounded-xl font-semibold text-white px-8 shadow-lg transition-all hover:opacity-90 hover:shadow-xl flex items-center justify-center gap-2"
                style={{ background: "var(--gradient-button)" }}
              >
                 Create your account  <UserPlus className="h-5 w-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button
                size="lg"
                variant="outline"
                className="rounded-xl px-8 border-[color:var(--brand-indigo)]/30 border-[color:var(--brand-indigo)]/60 bg-brand-yellow backdrop-blur flex items-center justify-center gap-2"
              >
                 I already have an account  <LogIn className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </section>

        {/*Feature cards */}
        <section className="mx-auto max-w-6xl px-6 pb-24">
          <div className="flex flex-col gap-4 sm:flex-row">
            {features.map((feat) => (
              <div
                key={feat.title}
                className="flex-1 rounded-2xl border border-[color:var(--brand-indigo)]/10 bg-white/70 p-6 backdrop-blur transition-all hover:-translate-y-1"
                style={{ boxShadow: "var(--shadow-soft)" }}
              >
                <div className="mb-4 text-3xl">{feat.icon}</div>
                <h3 className="mb-2 font-display text-lg font-semibold text-foreground">
                  {feat.title}
                </h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {feat.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section
          className="relative overflow-hidden py-20 text-center text-white"
          style={{ background: "var(--gradient-panel)" }}
        >

          <div
            className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full blur-xl"
            style={{ background: "radial-gradient(circle, #FFD230 0%, transparent 70%)", opacity: 0.35 }}
          />
          <div
            className="pointer-events-none absolute -left-20 bottom-0 h-64 w-64 rounded-full blur-xl"
            style={{ background: "radial-gradient(circle, #4b4eb8 0%, transparent 70%)", opacity: 0.5 }}
          />
          {/* subtle grid */}
          <div
            className="pointer-events-none absolute inset-0 opacity-[0.06]"
            style={{
              backgroundImage:
                "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
              backgroundSize: "32px 32px",
            }}
          />

          <div className="relative mx-auto max-w-2xl px-6">
            <div
              className="mx-auto mb-6 h-1 w-12 rounded-full"
              style={{ background: "var(--brand-yellow)" }}
            />
            <h2 className="font-display text-4xl font-semibold leading-tight">
              Ready to start your journey?
            </h2>
            <p className="mt-4 text-base text-white/80">
              Browse our curated learning paths and find the right one for you.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">

              <Link to="/register">
                <Button
                  size="lg"
                  variant="outline"
                  className="rounded-xl border-white/40 bg-transparent px-8 text-white hover:bg-[var(--brand-yellow)] hover:text-[color:var(--brand-indigo)] flex items-center justify-center gap-2"
                >
                  <UserPlus className="h-5 w-5" /> Create an account
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* ─── FOOTER ─── */}
      <footer className="relative z-10 border-t border-border/70 bg-white/60 py-8 backdrop-blur">
        <div className="mx-auto max-w-6xl px-6 text-xs text-muted-foreground">
          Rise Together · A Barabari Collective project
        </div>
      </footer>
    </div>
  );
};

export default Home;
