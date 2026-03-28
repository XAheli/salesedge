import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("[ErrorBoundary] Caught error:", error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    if (this.props.fallback) {
      return this.props.fallback;
    }

    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center px-4 py-16 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-risk-bg">
          <AlertTriangle className="h-8 w-8 text-risk" />
        </div>

        <h2 className="mt-6 font-display text-xl font-semibold text-text-primary">
          Something went wrong
        </h2>
        <p className="mt-2 max-w-md text-sm text-text-secondary">
          An unexpected error occurred while rendering this section. You can try
          refreshing, or contact support if the problem persists.
        </p>

        {this.state.error && (
          <details className="mt-4 max-w-lg text-left">
            <summary className="cursor-pointer text-xs font-medium text-text-tertiary hover:text-text-secondary">
              Technical details
            </summary>
            <pre className="mt-2 overflow-auto rounded-md bg-neutral-bg p-3 font-mono text-xs text-text-secondary">
              {this.state.error.message}
              {this.state.error.stack && `\n\n${this.state.error.stack}`}
            </pre>
          </details>
        )}

        <button
          onClick={this.handleRetry}
          className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
        >
          <RefreshCw size={16} />
          Try again
        </button>
      </div>
    );
  }
}
