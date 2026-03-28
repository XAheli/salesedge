import { useState } from "react";
import { useAppStore } from "@/stores/useAppStore";
import { Save, Key, Bell, User, Moon, Sun, Eye, EyeOff, CheckCircle2 } from "lucide-react";

export default function Settings() {
  const {
    theme,
    toggleTheme,
    userProfile,
    updateProfile,
    apiKeys,
    updateApiKeys,
    notificationPrefs,
    updateNotificationPrefs,
  } = useAppStore();

  const [saved, setSaved] = useState(false);
  const [showKeys, setShowKeys] = useState(false);

  function handleSave() {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  const NOTIF_TOGGLES = [
    { key: "dealRiskAlerts" as const, label: "Deal Risk Alerts", desc: "Get notified when a deal's risk score exceeds threshold" },
    { key: "churnWarnings" as const, label: "Churn Warnings", desc: "Alerts when customer churn probability increases" },
    { key: "dataFreshness" as const, label: "Data Freshness Alerts", desc: "Notify when data sources become stale" },
    { key: "dailyDigest" as const, label: "Daily Digest", desc: "Receive a daily email summary of pipeline changes" },
    { key: "emailAlerts" as const, label: "Email Alerts", desc: "Send alerts to your email address" },
    { key: "slackIntegration" as const, label: "Slack Integration", desc: "Push alerts to a Slack channel" },
  ];

  const API_KEY_FIELDS = [
    { key: "ogd" as const, label: "OGD India (data.gov.in)", placeholder: "Enter data.gov.in API key..." },
    { key: "openrouter" as const, label: "OpenRouter (AI Agents)", placeholder: "sk-or-v1-..." },
    { key: "finnhub" as const, label: "Finnhub", placeholder: "Enter Finnhub API key..." },
    { key: "alphaVantage" as const, label: "Alpha Vantage", placeholder: "Enter Alpha Vantage key..." },
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-text-primary">Settings</h2>
          <p className="mt-1 text-sm text-text-secondary">Manage your account, API keys, and notification preferences.</p>
        </div>
        <button
          onClick={handleSave}
          className="inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600 transition-colors"
        >
          {saved ? <CheckCircle2 size={16} /> : <Save size={16} />}
          {saved ? "Saved!" : "Save Changes"}
        </button>
      </div>

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <User size={18} className="text-primary-500" />
          <h3 className="text-sm font-semibold uppercase tracking-wider text-text-secondary">Profile</h3>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Full Name</label>
            <input
              type="text"
              value={userProfile.name}
              onChange={(e) => updateProfile({ name: e.target.value })}
              placeholder="Enter your name..."
              className="h-9 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-300 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Email</label>
            <input
              type="email"
              value={userProfile.email}
              onChange={(e) => updateProfile({ email: e.target.value })}
              placeholder="you@company.com"
              className="h-9 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-300 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Role</label>
            <select
              value={userProfile.role}
              onChange={(e) => updateProfile({ role: e.target.value })}
              className="h-9 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary focus:border-primary-300 focus:outline-none"
            >
              <option>Admin</option>
              <option>Sales Manager</option>
              <option>Sales Rep</option>
              <option>Analyst</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Timezone</label>
            <input
              type="text"
              value={userProfile.timezone}
              readOnly
              className="h-9 w-full rounded-lg border border-neutral-bg bg-neutral-bg px-3 text-sm text-text-tertiary"
            />
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          {theme === "dark" ? <Moon size={18} className="text-primary-500" /> : <Sun size={18} className="text-primary-500" />}
          <h3 className="text-sm font-semibold uppercase tracking-wider text-text-secondary">Appearance</h3>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-text-primary">Dark Mode</p>
            <p className="text-xs text-text-tertiary">Toggle between light and dark themes</p>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative h-6 w-11 rounded-full transition-colors ${theme === "dark" ? "bg-primary-500" : "bg-neutral"}`}
          >
            <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${theme === "dark" ? "left-[22px]" : "left-0.5"}`} />
          </button>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Key size={18} className="text-primary-500" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-text-secondary">API Keys</h3>
          </div>
          <button onClick={() => setShowKeys(!showKeys)} className="flex items-center gap-1 text-xs text-text-tertiary hover:text-text-secondary">
            {showKeys ? <EyeOff size={14} /> : <Eye size={14} />}
            {showKeys ? "Hide" : "Show"}
          </button>
        </div>
        <div className="space-y-3">
          {API_KEY_FIELDS.map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className="block text-xs font-medium text-text-secondary mb-1">{label}</label>
              <input
                type={showKeys ? "text" : "password"}
                value={apiKeys[key]}
                onChange={(e) => updateApiKeys({ [key]: e.target.value })}
                placeholder={placeholder}
                className="h-9 w-full rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm text-text-primary font-mono focus:border-primary-300 focus:outline-none"
              />
            </div>
          ))}
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Bell size={18} className="text-primary-500" />
          <h3 className="text-sm font-semibold uppercase tracking-wider text-text-secondary">Notifications</h3>
        </div>
        <div className="space-y-3">
          {NOTIF_TOGGLES.map(({ key, label, desc }) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-primary">{label}</p>
                <p className="text-xs text-text-tertiary">{desc}</p>
              </div>
              <button
                onClick={() => updateNotificationPrefs({ [key]: !notificationPrefs[key] })}
                className={`relative h-6 w-11 rounded-full transition-colors ${notificationPrefs[key] ? "bg-primary-500" : "bg-neutral"}`}
              >
                <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${notificationPrefs[key] ? "left-[22px]" : "left-0.5"}`} />
              </button>
            </div>
          ))}
          <div className="pt-2 border-t border-neutral-bg">
            <label className="block text-xs font-medium text-text-secondary mb-1">Risk Alert Threshold (%)</label>
            <input
              type="range"
              min="10"
              max="90"
              step="5"
              value={notificationPrefs.riskThreshold}
              onChange={(e) => updateNotificationPrefs({ riskThreshold: Number(e.target.value) })}
              className="w-full accent-primary-500"
            />
            <p className="text-xs text-text-tertiary">Alert when deal risk exceeds {notificationPrefs.riskThreshold}%</p>
          </div>
        </div>
      </div>
    </div>
  );
}
