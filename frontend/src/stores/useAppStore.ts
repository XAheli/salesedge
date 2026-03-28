import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Notification {
  id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export interface UserProfile {
  name: string;
  email: string;
  role: string;
  timezone: string;
  initials: string;
}

export interface UserApiKeys {
  ogd: string;
  openrouter: string;
  finnhub: string;
  alphaVantage: string;
}

export interface NotificationPrefs {
  dealRiskAlerts: boolean;
  churnWarnings: boolean;
  dataFreshness: boolean;
  dailyDigest: boolean;
  slackIntegration: boolean;
  emailAlerts: boolean;
  riskThreshold: number;
}

interface AppState {
  isAuthenticated: boolean;
  sidebarOpen: boolean;
  theme: "light" | "dark";
  notifications: Notification[];
  userProfile: UserProfile;
  apiKeys: UserApiKeys;
  notificationPrefs: NotificationPrefs;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleTheme: () => void;
  setTheme: (theme: "light" | "dark") => void;
  addNotification: (notification: Omit<Notification, "id" | "timestamp" | "read">) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  clearNotifications: () => void;
  updateProfile: (profile: Partial<UserProfile>) => void;
  updateApiKeys: (keys: Partial<UserApiKeys>) => void;
  updateNotificationPrefs: (prefs: Partial<NotificationPrefs>) => void;
  login: (profile: UserProfile) => void;
  register: (profile: UserProfile) => void;
  logout: () => void;
}

function computeInitials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      sidebarOpen: true,
      theme: "light",
      notifications: [],
      userProfile: {
        name: "",
        email: "",
        role: "Admin",
        timezone: "Asia/Kolkata (IST)",
        initials: "SE",
      },
      apiKeys: {
        ogd: "",
        openrouter: "",
        finnhub: "",
        alphaVantage: "",
      },
      notificationPrefs: {
        dealRiskAlerts: true,
        churnWarnings: true,
        dataFreshness: true,
        dailyDigest: false,
        slackIntegration: false,
        emailAlerts: true,
        riskThreshold: 50,
      },

      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      toggleTheme: () =>
        set((s) => ({ theme: s.theme === "light" ? "dark" : "light" })),
      setTheme: (theme) => set({ theme }),

      addNotification: (notif) =>
        set((s) => ({
          notifications: [
            {
              ...notif,
              id: crypto.randomUUID(),
              timestamp: new Date().toISOString(),
              read: false,
            },
            ...s.notifications,
          ].slice(0, 100),
        })),

      markNotificationRead: (id) =>
        set((s) => ({
          notifications: s.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n,
          ),
        })),

      markAllNotificationsRead: () =>
        set((s) => ({
          notifications: s.notifications.map((n) => ({ ...n, read: true })),
        })),

      clearNotifications: () => set({ notifications: [] }),

      updateProfile: (partial) =>
        set((s) => {
          const merged = { ...s.userProfile, ...partial };
          if (partial.name !== undefined) {
            merged.initials = computeInitials(merged.name) || "SE";
          }
          return { userProfile: merged };
        }),

      updateApiKeys: (partial) =>
        set((s) => ({ apiKeys: { ...s.apiKeys, ...partial } })),

      updateNotificationPrefs: (partial) =>
        set((s) => ({ notificationPrefs: { ...s.notificationPrefs, ...partial } })),

      login: (profile) =>
        set({
          isAuthenticated: true,
          userProfile: { ...profile, initials: computeInitials(profile.name) || "SE" },
        }),

      register: (profile) =>
        set({
          isAuthenticated: true,
          userProfile: { ...profile, initials: computeInitials(profile.name) || "SE" },
        }),

      logout: () =>
        set({
          isAuthenticated: false,
          userProfile: { name: "", email: "", role: "Admin", timezone: "Asia/Kolkata (IST)", initials: "SE" },
        }),
    }),
    {
      name: "salesedge-app",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        sidebarOpen: state.sidebarOpen,
        theme: state.theme,
        userProfile: state.userProfile,
        apiKeys: state.apiKeys,
        notificationPrefs: state.notificationPrefs,
      }),
    },
  ),
);
