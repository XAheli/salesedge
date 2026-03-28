import { useRoutes } from "react-router-dom";
import { Toaster } from "sonner";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import { routes } from "@/router";
import { useAppStore } from "@/stores/useAppStore";

export function App() {
  const theme = useAppStore((s) => s.theme);
  const routeElement = useRoutes(routes);

  return (
    <div data-theme={theme} className="min-h-screen bg-surface-background text-text-primary">
      <ErrorBoundary>
        {routeElement}
      </ErrorBoundary>
      <Toaster
        position="bottom-right"
        richColors
        toastOptions={{
          className: "font-sans",
        }}
      />
    </div>
  );
}
