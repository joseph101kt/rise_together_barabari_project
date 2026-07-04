import React from "react";
import  Logo  from "./Logo";

const AuthLayout=({ title, subtitle, children, footer }) => {
  return (
    <div className="grid min-h-screen w-full lg:grid-cols-2">
      <aside
        className="relative hidden flex-col justify-between overflow-hidden p-12 lg:flex"
        style={{ background: "var(--gradient-panel)", color: "#ffffff" }}
      >
        <div
          className="pointer-events-none absolute -right-40 -top-40 h-[28rem] w-[28rem] rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, #FFD230 0%, transparent 70%)", opacity: 0.35 }}
        />
        <div
          className="pointer-events-none absolute -bottom-48 -left-32 h-[28rem] w-[28rem] rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, #4b4eb8 0%, transparent 70%)", opacity: 0.6 }}
        />
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />

        <div className="relative z-10">
          <Logo className="text-white [&_span:last-child]:text-white [&_span:first-child]:!bg-[var(--brand-yellow)] [&_span:first-child]:!text-[var(--brand-indigo)]" />
        </div>

        <div className="relative z-10 space-y-7">
          <div className="h-1 w-16 rounded-full" style={{ background: "var(--brand-yellow)" }} />
          <h1 className="font-display text-5xl font-semibold leading-[1.05]">
            Learn together.
            <br />
            <span style={{ color: "var(--brand-yellow)" }}>Rise together.</span>
          </h1>
          <p className="max-w-md text-base/relaxed text-white/85">
            A community learning platform for students at government colleges in India —
            curated paths, peer accountability, and real human feedback on real work.
          </p>
          <ul className="space-y-3 text-sm text-white/90">
            {[
              "Curated paths from free internet resources",
              "Auto-assigned study groups of 5–6 peers",
              "Written project feedback from mentors",
            ].map((item) => (
              <li key={item} className="flex items-start gap-3">
                <span
                  className="mt-1.5 inline-block h-2 w-2 shrink-0 rounded-full"
                  style={{ background: "var(--brand-yellow)" }}
                />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <p className="relative z-10 text-xs text-white/60">
          A Barabari Collective · Workplace Readiness Lab 2025 project
        </p>
      </aside>

      <main className="relative flex min-h-screen flex-col bg-background">
        <header className="flex items-center justify-between p-6 lg:hidden">
          <Logo />
        </header>

        <div className="flex flex-1 items-center justify-center p-6 sm:p-10">
          <div
            className="w-full max-w-md space-y-7 rounded-2xl border border-[color:var(--brand-indigo)]/10 bg-card p-8 sm:p-10"
            style={{ boxShadow: "var(--shadow-elegant)" }}
          >
            <div className="space-y-3">
              <div className="h-1 w-10 rounded-full" style={{ background: "var(--brand-yellow)" }} />
              <h2 className="font-display text-3xl font-semibold tracking-tight text-foreground">
                {title}
              </h2>
              {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
            </div>

            {children}

            {footer ? (
              <div className="pt-2 text-center text-sm text-muted-foreground">{footer}</div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}

export default AuthLayout;