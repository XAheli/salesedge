import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface-background px-4 text-center">
      <h1 className="font-display text-7xl font-bold text-primary-500">404</h1>
      <p className="mt-4 text-lg font-medium text-text-primary">Page not found</p>
      <p className="mt-2 text-sm text-text-secondary">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link
        to="/"
        className="mt-8 inline-flex rounded-lg bg-primary-500 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-600"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}
