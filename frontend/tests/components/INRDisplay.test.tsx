import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { INRDisplay } from "@/components/indian-context/INRDisplay";

describe("INRDisplay", () => {
  it("renders a basic INR value", () => {
    render(<INRDisplay value={100000} />);
    const el = screen.getByText(/₹/);
    expect(el).toBeInTheDocument();
  });

  it("renders with compact notation for crores", () => {
    render(<INRDisplay value={50000000} compact />);
    const el = screen.getByText(/Cr/);
    expect(el).toBeInTheDocument();
  });

  it("renders with compact notation for lakhs", () => {
    render(<INRDisplay value={500000} compact />);
    const el = screen.getByText(/L/);
    expect(el).toBeInTheDocument();
  });

  it("renders with compact notation for thousands", () => {
    render(<INRDisplay value={5000} compact />);
    const el = screen.getByText(/K/);
    expect(el).toBeInTheDocument();
  });

  it("renders full format with Indian number grouping", () => {
    render(<INRDisplay value={1234567} />);
    const el = screen.getByText(/12,34,567/);
    expect(el).toBeInTheDocument();
  });

  it("hides symbol when showSymbol is false", () => {
    render(<INRDisplay value={1000} showSymbol={false} />);
    const el = screen.getByText(/1,000/);
    expect(el.textContent).not.toContain("₹");
  });

  it("shows symbol by default", () => {
    render(<INRDisplay value={1000} />);
    const el = screen.getByText(/₹/);
    expect(el).toBeInTheDocument();
  });

  it("applies sm size class", () => {
    render(<INRDisplay value={1000} size="sm" />);
    const el = screen.getByText(/₹/);
    expect(el).toHaveClass("text-sm");
  });

  it("applies md size class by default", () => {
    render(<INRDisplay value={1000} />);
    const el = screen.getByText(/₹/);
    expect(el).toHaveClass("text-base");
  });

  it("applies lg size class", () => {
    render(<INRDisplay value={1000} size="lg" />);
    const el = screen.getByText(/₹/);
    expect(el).toHaveClass("text-xl");
  });

  it("applies custom className", () => {
    render(<INRDisplay value={1000} className="my-custom" />);
    const el = screen.getByText(/₹/);
    expect(el).toHaveClass("my-custom");
  });

  it("has tabular-nums class for proper number alignment", () => {
    render(<INRDisplay value={1000} />);
    const el = screen.getByText(/₹/);
    expect(el).toHaveClass("tabular-nums");
  });

  it("has title attribute with full formatted value", () => {
    render(<INRDisplay value={5000000} compact />);
    const el = screen.getByText(/Cr/);
    expect(el).toHaveAttribute("title");
    expect(el.getAttribute("title")).toContain("₹");
  });

  it("handles zero value", () => {
    render(<INRDisplay value={0} />);
    const el = screen.getByText(/₹/);
    expect(el).toBeInTheDocument();
  });

  it("handles negative values", () => {
    render(<INRDisplay value={-500000} compact />);
    const el = screen.getByText(/-/);
    expect(el).toBeInTheDocument();
  });

  it("handles very large values (lakh crores)", () => {
    render(<INRDisplay value={1000000000000} compact />);
    const el = screen.getByText(/Cr/);
    expect(el).toBeInTheDocument();
  });

  it("renders correctly with custom decimals", () => {
    render(<INRDisplay value={1234567} compact decimals={0} />);
    const el = screen.getByText(/₹/);
    expect(el).toBeInTheDocument();
  });
});
