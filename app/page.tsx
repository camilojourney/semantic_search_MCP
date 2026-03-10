export default function Home() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 border-b border-gray-800/50 bg-[#0a0a0a]/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <span className="text-xl font-bold tracking-tight">Holusight</span>
          <a
            href="mailto:juancamilomabe@gmail.com"
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-violet-500 text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Request Demo
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-40 pb-32 px-6 overflow-hidden">
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            Enterprise AI Orchestration
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-[1.1] mb-6">
            Enterprise AI that actually works.{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
              Reliable by design.
            </span>
          </h1>

          <p className="text-lg text-gray-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            Holus orchestrates your AI agents with deterministic pipelines,
            multi-model routing, and full observability. No black boxes. No
            hallucination cascades.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <a
              href="mailto:juancamilomabe@gmail.com"
              className="px-6 py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-violet-500 font-medium hover:opacity-90 transition-opacity"
            >
              Request Demo
            </a>
            <a
              href="#how-it-works"
              className="group flex items-center gap-2 text-gray-300 hover:text-white transition-colors font-medium"
            >
              See How It Works
              <svg
                className="w-4 h-4 group-hover:translate-x-0.5 transition-transform"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </a>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-24 px-6 border-t border-gray-800/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-red-500/30 bg-red-500/10 text-red-300 text-sm font-medium mb-6">
              The Enterprise AI Problem
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              AI deployments fail at scale — silently.
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Most enterprise AI projects produce unpredictable outputs, no visibility
              into failures, and fragile pipelines that break in production.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-7 rounded-2xl bg-gray-900/60 border border-gray-800">
              <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-white mb-2">Unpredictable outputs</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Teams deploy AI and get different results every run. No way to know
                if an output is correct until it's already in production.
              </p>
            </div>

            <div className="p-7 rounded-2xl bg-gray-900/60 border border-gray-800">
              <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-white mb-2">Zero visibility</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                When an AI pipeline fails, no one knows what step broke, which model
                was responsible, or how to reproduce the error.
              </p>
            </div>

            <div className="p-7 rounded-2xl bg-gray-900/60 border border-gray-800">
              <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-white mb-2">Hallucinations go uncaught</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Models hallucinate and no one catches it. One bad output cascades
                into the next step, compounding the error silently.
              </p>
            </div>

            <div className="p-7 rounded-2xl bg-gray-900/60 border border-gray-800">
              <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-white mb-2">Every team rebuilds from scratch</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Engineering, content, and data teams all build their own fragile
                AI pipelines. No shared standards, no reuse, no institutional knowledge.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section id="features" className="py-24 px-6 border-t border-gray-800/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-6">
              How Holus Changes This
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Built for reliability, not just capability.
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Every component of Holus is designed for production environments where
              accuracy, auditability, and reliability are non-negotiable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-8 rounded-2xl bg-gray-900 border border-gray-800 hover:border-indigo-500/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center mb-5">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-3">Phase-Gated Pipelines</h3>
              <p className="text-gray-400 leading-relaxed">
                Every step is verified before the next one runs. If a step fails
                the gate, the pipeline stops — not cascades. No hallucination
                snowballs reach production.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-gray-900 border border-gray-800 hover:border-violet-500/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center mb-5">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-3">Multi-Model Routing</h3>
              <p className="text-gray-400 leading-relaxed">
                Automatically routes each task to the right model — Claude for
                reasoning, Gemini for research, Codex for code. The best model
                for each job, without manual configuration.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-gray-900 border border-gray-800 hover:border-indigo-500/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center mb-5">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-3">Full Observability</h3>
              <p className="text-gray-400 leading-relaxed">
                Every agent run is logged, scored, and auditable. Know exactly
                what ran, which model was used, what the output was, and why
                it passed or failed the gate.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-gray-900 border border-gray-800 hover:border-violet-500/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center mb-5">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-3">Federated Deployment</h3>
              <p className="text-gray-400 leading-relaxed">
                Deploy AI agents across distributed teams without a centralized
                bottleneck. Each department gets agents tuned for their workflows.
                No rip-and-replace — integrates via API.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 border-t border-gray-800/50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-6">
              How It Works
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              Three steps to reliable AI.
            </h2>
          </div>

          <div className="relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute left-[39px] top-12 bottom-12 w-px bg-gradient-to-b from-indigo-500/40 via-violet-500/40 to-indigo-500/10" />

            <div className="space-y-12">
              {/* Step 1 */}
              <div className="flex gap-8 items-start">
                <div className="flex-shrink-0 w-20 flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 flex items-center justify-center text-sm font-bold z-10">
                    1
                  </div>
                </div>
                <div className="pb-4">
                  <h3 className="text-xl font-semibold mb-3">Connect</h3>
                  <p className="text-gray-400 leading-relaxed max-w-lg">
                    Connect Holus to your existing stack via API. No infrastructure
                    migration required. Works with your current tools, models, and
                    data sources out of the box.
                  </p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex gap-8 items-start">
                <div className="flex-shrink-0 w-20 flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 flex items-center justify-center text-sm font-bold z-10">
                    2
                  </div>
                </div>
                <div className="pb-4">
                  <h3 className="text-xl font-semibold mb-3">Orchestrate</h3>
                  <p className="text-gray-400 leading-relaxed max-w-lg">
                    Define your pipelines with phase-gated verification steps. Holus
                    routes each task to the right model, runs verification gates at
                    each step, and stops on failure — not cascades.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex gap-8 items-start">
                <div className="flex-shrink-0 w-20 flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 flex items-center justify-center text-sm font-bold z-10">
                    3
                  </div>
                </div>
                <div className="pb-4">
                  <h3 className="text-xl font-semibold mb-3">Observe</h3>
                  <p className="text-gray-400 leading-relaxed max-w-lg">
                    Every run is logged, scored, and auditable from a single
                    dashboard. See exactly what each agent did, which model ran it,
                    and how quality has trended over time.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-24 px-6 border-t border-gray-800/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-6">
              Use Cases
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Built for teams that ship.
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Holus works wherever teams are deploying AI today — without requiring
              you to change how you build.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Engineering */}
            <div className="p-8 rounded-2xl bg-gray-900 border border-gray-800 hover:border-indigo-500/50 transition-colors flex flex-col">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center mb-5">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-3">Engineering Teams</h3>
              <p className="text-gray-400 leading-relaxed text-sm flex-1">
                Automate code review, spec validation, and PR summaries with
                agents that verify their own outputs before reporting back.
                Every comment is traceable to the model that generated it.
              </p>
            </div>

            {/* Content */}
            <div className="p-8 rounded-2xl bg-gray-900 border border-gray-800 hover:border-violet-500/50 transition-colors flex flex-col">
              <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center mb-5">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5M6 7.5h3v3H6v-3z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-3">Content Teams</h3>
              <p className="text-gray-400 leading-relaxed text-sm flex-1">
                Generate content at scale with quality gates at every step.
                Brand voice checks, factual verification, and approval workflows
                — before anything gets published.
              </p>
            </div>

            {/* Data */}
            <div className="p-8 rounded-2xl bg-gray-900 border border-gray-800 hover:border-indigo-500/50 transition-colors flex flex-col">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center mb-5">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 2.25v-2.25m0 6v-2.25m0 6v-2.25M3.75 8.625v-2.25m0 6v-2.25m0 6v-2.25" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-3">Data Teams</h3>
              <p className="text-gray-400 leading-relaxed text-sm flex-1">
                Run AI-driven data pipelines with deterministic verification at
                each transformation step. Catch anomalies and model drift before
                they reach downstream consumers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="early-access" className="py-32 px-6 border-t border-gray-800/50">
        <div className="relative max-w-2xl mx-auto text-center">
          <div className="absolute inset-0 -z-10 bg-indigo-600/10 rounded-3xl blur-[60px]" />
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-5">
            Ready to deploy AI that works?
          </h2>
          <p className="text-gray-400 text-lg mb-10 leading-relaxed">
            Holus is in early access. Join engineering and product teams already
            building with deterministic AI pipelines.
          </p>
          <a
            href="mailto:juancamilomabe@gmail.com"
            className="inline-block px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 text-lg font-semibold hover:opacity-90 transition-opacity"
          >
            Request Early Access
          </a>
          <p className="mt-5 text-sm text-gray-500">
            No setup fee. Onboarding included.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <span className="text-sm font-semibold tracking-tight">Holusight</span>
          <p className="text-sm text-gray-500">
            Built by{" "}
            <a
              href="https://camilomartinez.co"
              className="text-gray-400 hover:text-white transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              Juan Camilo Martinez
            </a>
            {" "}|{" "}
            <a
              href="https://camilomartinez.co"
              className="text-gray-400 hover:text-white transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              camilomartinez.co
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
