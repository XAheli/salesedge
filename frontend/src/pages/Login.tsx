import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "@/stores/useAppStore";
import { post } from "@/api/client";
import { ArrowRight, UserPlus, LogIn } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const { login, register } = useAppStore();
  const [mode, setMode] = useState<"welcome" | "register" | "login">("welcome");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("Admin");
  const [org, setOrg] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await post<{ token: string; user: { name: string; email: string; role: string; initials: string } }>(
        "/v1/auth/register",
        { name, email, password, role, organization: org },
      );
      const { token, user } = result.data;
      localStorage.setItem("salesedge-token", token);
      register({
        name: user.name,
        email: user.email,
        role: user.role,
        timezone: "Asia/Kolkata (IST)",
        initials: user.initials,
      });
      navigate("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await post<{ token: string; user: { name: string; email: string; role: string; initials: string } }>(
        "/v1/auth/login",
        { email, password },
      );
      const { token, user } = result.data;
      localStorage.setItem("salesedge-token", token);
      login({
        name: user.name,
        email: user.email,
        role: user.role,
        timezone: "Asia/Kolkata (IST)",
        initials: user.initials,
      });
      navigate("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (mode === "welcome") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 via-surface-background to-primary-100 px-4">
        <div className="w-full max-w-lg text-center">
          <img src="/logo.svg" alt="SalesEdge" className="mx-auto h-16 w-16 drop-shadow-lg" />
          <h1 className="mt-4 font-display text-4xl font-bold text-text-primary">SalesEdge</h1>
          <p className="mt-2 text-lg text-text-secondary">Intelligent Sales & Revenue Operations Platform</p>
          <p className="mt-1 text-sm text-text-tertiary">
            India-focused AI platform for enterprise sales teams
          </p>

          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <button
              onClick={() => setMode("register")}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary-500 px-6 py-3 text-sm font-semibold text-white shadow-md transition-all hover:bg-primary-600 hover:shadow-lg"
            >
              <UserPlus size={18} />
              Get Started
              <ArrowRight size={16} />
            </button>
            <button
              onClick={() => setMode("login")}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-neutral-bg bg-surface-card px-6 py-3 text-sm font-semibold text-text-primary shadow-sm transition-all hover:bg-neutral-bg"
            >
              <LogIn size={18} />
              Sign In
            </button>
          </div>

          <div className="mt-16 grid grid-cols-3 gap-6 text-center">
            {[
              { stat: "25+", label: "API Integrations" },
              { stat: "4", label: "AI Agents" },
              { stat: "100%", label: "India Focused" },
            ].map(({ stat, label }) => (
              <div key={label}>
                <p className="font-display text-2xl font-bold text-primary-600">{stat}</p>
                <p className="mt-1 text-xs text-text-tertiary">{label}</p>
              </div>
            ))}
          </div>

          <div className="mt-12 border-t border-neutral-bg pt-6">
            <a
              href="https://github.com/XAheli/salesedge"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-text-tertiary hover:text-primary-500 transition-colors"
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
              Check us out on GitHub
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (mode === "register") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 via-surface-background to-primary-100 px-4">
        <div className="w-full max-w-md">
          <div className="text-center">
            <h1 className="font-display text-3xl font-bold text-primary-600">SalesEdge</h1>
            <p className="mt-2 text-sm text-text-secondary">Create your account</p>
          </div>

          <form onSubmit={handleRegister} className="card mt-8 space-y-4 p-6">
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Full Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Priya Sharma"
                className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Work Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Organization</label>
              <input
                type="text"
                value={org}
                onChange={(e) => setOrg(e.target.value)}
                placeholder="Your company name"
                className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none"
              >
                <option>Admin</option>
                <option>Sales Manager</option>
                <option>Sales Rep</option>
                <option>Analyst</option>
                <option>CXO / Executive</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Password</label>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 6 characters"
                className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>

            {error && <p className="rounded-lg bg-risk/10 px-3 py-2 text-xs text-risk">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-primary-500 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-primary-600 disabled:opacity-50"
            >
              {loading ? "Creating account..." : "Create Account"}
            </button>

            <p className="text-center text-xs text-text-tertiary">
              Already have an account?{" "}
              <button type="button" onClick={() => setMode("login")} className="font-medium text-primary-500 hover:text-primary-600">
                Sign in
              </button>
            </p>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 via-surface-background to-primary-100 px-4">
      <div className="w-full max-w-md">
        <div className="text-center">
          <h1 className="font-display text-3xl font-bold text-primary-600">SalesEdge</h1>
          <p className="mt-2 text-sm text-text-secondary">Sign in to your account</p>
        </div>

        <form onSubmit={handleLogin} className="card mt-8 space-y-4 p-6">
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          {error && <p className="rounded-lg bg-risk/10 px-3 py-2 text-xs text-risk">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-primary-500 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-primary-600 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <p className="text-center text-xs text-text-tertiary">
            Don't have an account?{" "}
            <button type="button" onClick={() => setMode("register")} className="font-medium text-primary-500 hover:text-primary-600">
              Get started
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}
