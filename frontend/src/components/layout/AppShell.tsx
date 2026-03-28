import { type ReactNode, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Target,
  BarChart3,
  RefreshCw,
  Swords,
  Database,
  Settings,
  Search,
  Bell,
  Moon,
  Sun,
  Menu,
  X,
  Bot,
} from "lucide-react";
import { useAppStore } from "@/stores/useAppStore";
import { CommandPalette } from "@/components/shared/CommandPalette";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";

const NAV_ITEMS = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/prospects", label: "Prospects", icon: Target },
  { path: "/deals", label: "Deals", icon: BarChart3 },
  { path: "/retention", label: "Retention", icon: RefreshCw },
  { path: "/intelligence", label: "Intelligence", icon: Swords },
  { path: "/agents", label: "AI Agents", icon: Bot },
  { path: "/data", label: "Data", icon: Database },
  { path: "/settings", label: "Settings", icon: Settings },
] as const;

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const {
    sidebarOpen,
    toggleSidebar,
    theme,
    toggleTheme,
    userProfile,
    notifications: storeNotifications,
    markAllNotificationsRead,
    logout,
  } = useAppStore();
  const location = useLocation();

  const pageTitle =
    NAV_ITEMS.find(
      (item) =>
        item.path === location.pathname ||
        (item.path !== "/" && location.pathname.startsWith(item.path)),
    )?.label ?? "SalesEdge";

  useKeyboardShortcuts();

  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const unreadCount = storeNotifications.filter((n) => !n.read).length;
  const notifications = storeNotifications.slice(0, 5).map((n) => ({
    title: n.title,
    time: n.timestamp
      ? new Date(n.timestamp).toLocaleString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true })
      : "",
  }));

  const displayName = userProfile.name || "Set up profile";
  const displayEmail = userProfile.email || "Go to Settings";
  const displayInitials = userProfile.initials || "SE";

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-40 flex flex-col bg-surface-sidebar transition-all duration-300
          ${sidebarOpen ? "w-56" : "w-16"}
          lg:relative
        `}
      >
        <div className={`flex h-14 items-center ${sidebarOpen ? "justify-between px-4" : "justify-center"}`}>
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <img src="/logo.svg" alt="SalesEdge" className="h-7 w-7" />
              <span className="font-display text-lg font-bold text-stone-50">
                SalesEdge
              </span>
            </div>
          )}
          <button
            onClick={toggleSidebar}
            className="rounded-md p-1.5 text-stone-400 hover:bg-white/10 hover:text-stone-50"
            aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        <nav className="mt-2 flex flex-1 flex-col gap-1 px-2" aria-label="Main navigation">
          {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-surface-sidebar-active text-white"
                    : "text-stone-400 hover:bg-white/10 hover:text-stone-50"
                } ${!sidebarOpen ? "justify-center px-0" : ""}`
              }
              title={label}
            >
              <Icon size={20} />
              {sidebarOpen && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 p-3">
          <a
            href="https://github.com/XAheli/salesedge"
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-center gap-2 rounded-md px-2 py-1.5 text-xs text-stone-400 hover:bg-white/10 hover:text-stone-200 transition-colors ${!sidebarOpen ? "justify-center px-0" : ""}`}
            title="GitHub"
          >
            <svg className="h-4 w-4 shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            {sidebarOpen && <span>GitHub</span>}
          </a>
          {sidebarOpen && (
            <p className="mt-2 px-2 text-[10px] text-stone-600">v1.0.0 · MIT License</p>
          )}
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-14 shrink-0 items-center gap-4 border-b border-neutral-bg bg-surface-header px-4 lg:px-6">
          <h1 className="font-display text-lg font-semibold">{pageTitle}</h1>

          <div className="ml-auto flex items-center gap-2">
            {/* Search - opens command palette */}
            <div className="relative hidden sm:block">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
              <input
                type="text"
                placeholder="Search... (⌘K)"
                className="h-9 w-64 cursor-pointer rounded-lg border border-neutral-bg bg-neutral-bg/50 pl-9 pr-3 text-sm text-text-primary placeholder:text-text-tertiary focus:border-primary-300 focus:bg-surface-card focus:outline-none"
                readOnly
                onClick={() => window.dispatchEvent(new CustomEvent("salesedge:open-command-palette"))}
              />
            </div>

            {/* Notifications dropdown */}
            <div className="relative">
              <button
                onClick={() => setNotifOpen(!notifOpen)}
                className="relative rounded-lg p-2 text-text-secondary hover:bg-neutral-bg"
                aria-label="Notifications"
              >
                <Bell size={18} />
                {unreadCount > 0 && (
                  <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-risk text-[10px] font-bold text-white">
                    {unreadCount}
                  </span>
                )}
              </button>
              {notifOpen && (
                <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border border-neutral-bg bg-surface-card p-0 shadow-lg">
                  <div className="border-b border-neutral-bg px-4 py-3">
                    <p className="text-sm font-semibold text-text-primary">Notifications</p>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <p className="p-4 text-center text-xs text-text-tertiary">No new notifications</p>
                    ) : (
                      notifications.map((n, i) => (
                        <div key={i} className="border-b border-neutral-bg/50 px-4 py-3 hover:bg-neutral-bg/30 cursor-pointer" onClick={() => setNotifOpen(false)}>
                          <p className="text-sm text-text-primary">{n.title}</p>
                          <p className="mt-0.5 text-xs text-text-tertiary">{n.time}</p>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="border-t border-neutral-bg px-4 py-2">
                    <button className="text-xs font-medium text-primary-500 hover:text-primary-600" onClick={() => { setNotifOpen(false); markAllNotificationsRead(); }}>
                      Mark all as read
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="rounded-lg p-2 text-text-secondary hover:bg-neutral-bg"
              aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            >
              {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
            </button>

            {/* Profile dropdown */}
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-500 text-sm font-semibold text-white hover:bg-primary-600 transition-colors"
                aria-label="User menu"
              >
                {displayInitials}
              </button>
              {profileOpen && (
                <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-lg border border-neutral-bg bg-surface-card shadow-lg">
                  <div className="border-b border-neutral-bg px-4 py-3">
                    <p className="text-sm font-semibold text-text-primary">{displayName}</p>
                    <p className="text-xs text-text-tertiary">{displayEmail}</p>
                  </div>
                  <div className="p-1">
                    <a href="/settings" className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-text-secondary hover:bg-neutral-bg" onClick={() => setProfileOpen(false)}>
                      Settings
                    </a>
                    <button
                      onClick={() => { setProfileOpen(false); logout(); window.location.href = "/login"; }}
                      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-risk hover:bg-risk/5"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 scrollbar-thin">
          {children}
        </main>
      </div>

      <CommandPalette />
    </div>
  );
}
