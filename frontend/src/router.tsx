import { lazy, Suspense, type ReactNode } from "react";
import { Navigate } from "react-router-dom";
import type { RouteObject } from "react-router-dom";
import { useAppStore } from "@/stores/useAppStore";

function lazyPage(factory: () => Promise<{ default: React.ComponentType }>) {
  const Component = lazy(factory);
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Component />
    </Suspense>
  );
}

function PageSkeleton() {
  return (
    <div className="flex h-screen items-center justify-center bg-surface-background">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary-200 border-t-primary-500" />
        <p className="text-sm text-text-secondary">Loading...</p>
      </div>
    </div>
  );
}

const AppShell = lazy(() =>
  import("@/components/layout/AppShell").then((m) => ({ default: m.AppShell })),
);

function AuthGuard({ children }: { children: ReactNode }) {
  const isAuthenticated = useAppStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function ShellLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <Suspense fallback={<PageSkeleton />}>
        <AppShell>{children}</AppShell>
      </Suspense>
    </AuthGuard>
  );
}

function withShell(element: ReactNode): ReactNode {
  return <ShellLayout>{element}</ShellLayout>;
}

export const routes: RouteObject[] = [
  {
    path: "/login",
    element: lazyPage(() => import("@/pages/Login")),
  },
  {
    path: "/",
    element: withShell(lazyPage(() => import("@/pages/Dashboard"))),
  },
  {
    path: "/prospects",
    element: withShell(lazyPage(() => import("@/pages/Prospects"))),
  },
  {
    path: "/prospects/:id",
    element: withShell(lazyPage(() => import("@/pages/ProspectDetail"))),
  },
  {
    path: "/deals",
    element: withShell(lazyPage(() => import("@/pages/Deals"))),
  },
  {
    path: "/deals/:id",
    element: withShell(lazyPage(() => import("@/pages/DealDetail"))),
  },
  {
    path: "/retention",
    element: withShell(lazyPage(() => import("@/pages/Retention"))),
  },
  {
    path: "/intelligence",
    element: withShell(lazyPage(() => import("@/pages/Competitive"))),
  },
  {
    path: "/agents",
    element: withShell(lazyPage(() => import("@/pages/Agents"))),
  },
  {
    path: "/data",
    element: withShell(lazyPage(() => import("@/pages/DataProvenance"))),
  },
  {
    path: "/settings",
    element: withShell(lazyPage(() => import("@/pages/Settings"))),
  },
  {
    path: "*",
    element: lazyPage(() => import("@/pages/NotFound")),
  },
];
