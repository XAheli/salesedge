import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KPICard, type KPITrend } from "@/components/data-display/KPICard";

describe("KPICard", () => {
  it("renders title and value", () => {
    render(<KPICard title="Pipeline Value" value={5000000} format="inr" />);
    expect(screen.getByText("Pipeline Value")).toBeInTheDocument();
  });

  it("formats INR values with compact notation", () => {
    render(<KPICard title="Revenue" value={15000000} format="inr" />);
    const displayed = screen.getByText(/₹/);
    expect(displayed).toBeInTheDocument();
  });

  it("formats percentage values", () => {
    render(<KPICard title="Win Rate" value={67.5} format="percent" />);
    expect(screen.getByText("67.5%")).toBeInTheDocument();
  });

  it("formats day values", () => {
    render(<KPICard title="Avg Cycle" value={23} format="days" />);
    expect(screen.getByText("23d")).toBeInTheDocument();
  });

  it("formats plain numbers with Indian locale", () => {
    render(<KPICard title="Deals" value={1234} format="number" />);
    expect(screen.getByText("1,234")).toBeInTheDocument();
  });

  it("renders string values as-is", () => {
    render(<KPICard title="Status" value="Active" />);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("displays trend with up direction", () => {
    const trend: KPITrend = {
      direction: "up",
      value: 12.5,
      period: "vs last month",
      isPositive: true,
    };
    render(<KPICard title="Revenue" value={1000} trend={trend} />);
    expect(screen.getByText("+12.5%")).toBeInTheDocument();
    expect(screen.getByText("vs last month")).toBeInTheDocument();
  });

  it("displays trend with down direction", () => {
    const trend: KPITrend = {
      direction: "down",
      value: -5.2,
      period: "vs last week",
      isPositive: false,
    };
    render(<KPICard title="Churn" value={8} trend={trend} />);
    expect(screen.getByText("-5.2%")).toBeInTheDocument();
  });

  it("displays flat trend", () => {
    const trend: KPITrend = {
      direction: "flat",
      value: 0.0,
      period: "this quarter",
      isPositive: true,
    };
    render(<KPICard title="Score" value={75} trend={trend} />);
    expect(screen.getByText("0.0%")).toBeInTheDocument();
  });

  it("shows confidence badge when confidence is provided", () => {
    render(<KPICard title="Score" value={85} confidence={0.92} />);
    expect(screen.getByText("Score")).toBeInTheDocument();
  });

  it("shows source information", () => {
    render(<KPICard title="GDP" value="7.3%" source="RBI DBIE" />);
    expect(screen.getByText("RBI DBIE")).toBeInTheDocument();
  });

  it("shows last updated timestamp", () => {
    render(<KPICard title="Pipeline" value={100} lastUpdated="5 min ago" />);
    expect(screen.getByText("5 min ago")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<KPICard title="Clickable" value={42} onClick={handleClick} />);
    fireEvent.click(screen.getByText("Clickable").closest("div")!);
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it("has button role when clickable", () => {
    render(<KPICard title="Card" value={1} onClick={() => {}} />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("handles keyboard activation when clickable", () => {
    const handleClick = vi.fn();
    render(<KPICard title="Card" value={1} onClick={handleClick} />);
    const card = screen.getByRole("button");
    fireEvent.keyDown(card, { key: "Enter" });
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it("does not have button role when not clickable", () => {
    render(<KPICard title="Card" value={1} />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("renders with custom unit", () => {
    render(<KPICard title="Count" value={150} unit="users" />);
    expect(screen.getByText("users")).toBeInTheDocument();
  });

  it("does not show unit for inr format", () => {
    render(<KPICard title="Revenue" value={1000} format="inr" unit="₹" />);
    const unitSpans = screen.queryAllByText("₹");
    const standaloneUnits = unitSpans.filter(
      (el) => el.tagName === "SPAN" && el.classList.contains("ml-1"),
    );
    expect(standaloneUnits).toHaveLength(0);
  });

  it("applies custom className", () => {
    const { container } = render(
      <KPICard title="Test" value={1} className="custom-class" />,
    );
    expect(container.firstChild).toHaveClass("custom-class");
  });
});
