import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { get, post } from "@/api/client";
import { Bot, Send, Sparkles, Target, BarChart3, RefreshCw, Swords, Loader2, AlertTriangle, Key } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface AgentStatus {
  name: string;
  status: string;
  description: string;
  is_llm_configured: boolean;
  supported_actions: string[];
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  timestamp: string;
}

const AGENT_META: Record<string, { icon: typeof Bot; color: string; label: string; placeholder: string }> = {
  prospect: {
    icon: Target,
    color: "text-primary-500",
    label: "Prospect Agent",
    placeholder: "e.g. Analyze Infosys as a prospect for our SaaS platform...",
  },
  deal_intel: {
    icon: BarChart3,
    color: "text-info",
    label: "Deal Intel Agent",
    placeholder: "e.g. What are the risk factors for our HDFC Bank deal worth ₹12Cr?",
  },
  retention: {
    icon: RefreshCw,
    color: "text-revenue-positive",
    label: "Retention Agent",
    placeholder: "e.g. Predict churn risk for our top 5 customers...",
  },
  competitive: {
    icon: Swords,
    color: "text-data-quality",
    label: "Competitive Agent",
    placeholder: "e.g. Generate a battlecard comparing us vs Salesforce for the BFSI sector...",
  },
};

export default function Agents() {
  const navigate = useNavigate();
  const [selectedAgent, setSelectedAgent] = useState<string>("prospect");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const { data: statusData, isLoading: statusLoading } = useQuery({
    queryKey: ["agents", "status"],
    queryFn: () => get<AgentStatus[]>("/v1/agents/status"),
    refetchInterval: 30_000,
  });

  const agents: AgentStatus[] = (statusData as any)?.data ?? [];
  const isLLMConfigured = agents.length > 0 && agents[0]?.is_llm_configured;

  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      post<{ agent: string; response: string; model_used: string; is_configured: boolean }>(
        "/v1/agents/chat",
        { agent: selectedAgent, message },
      ),
    onSuccess: (data: any) => {
      const response = data?.data?.response ?? "No response received.";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response,
          agent: selectedAgent,
          timestamp: new Date().toISOString(),
        },
      ]);
    },
    onError: (err: Error) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${err.message}`,
          agent: selectedAgent,
          timestamp: new Date().toISOString(),
        },
      ]);
    },
  });

  function handleSend() {
    if (!input.trim()) return;
    const userMsg: ChatMessage = {
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    chatMutation.mutate(input.trim());
    setInput("");
  }

  const meta = AGENT_META[selectedAgent] ?? AGENT_META.prospect;
  const AgentIcon = meta.icon;

  return (
    <div className="flex h-[calc(100vh-3.5rem)] gap-4">
      {/* Agent Selector Sidebar */}
      <div className="w-64 shrink-0 space-y-2 overflow-y-auto">
        <h2 className="px-1 text-sm font-semibold uppercase tracking-wider text-text-secondary">
          AI Agents
        </h2>
        <p className="px-1 text-xs text-text-tertiary">
          Powered by LLM. Select an agent to start a conversation.
        </p>

        {!isLLMConfigured && !statusLoading && (
          <div className="rounded-lg border border-caution/30 bg-caution/5 p-3">
            <div className="flex items-start gap-2">
              <Key size={14} className="mt-0.5 shrink-0 text-caution" />
              <div>
                <p className="text-xs font-medium text-caution">LLM not configured</p>
                <p className="mt-0.5 text-[11px] text-text-tertiary">
                  Set an LLM API key in{" "}
                  <button
                    onClick={() => navigate("/settings")}
                    className="font-medium text-primary-500 hover:text-primary-600"
                  >
                    Settings
                  </button>
                  . Supports OpenRouter, Groq (free), OpenAI, or Ollama (local).
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-1">
          {Object.entries(AGENT_META).map(([key, { icon: Icon, color, label }]) => {
            const status = agents.find((a) => a.name === `${key}_agent`);
            return (
              <button
                key={key}
                onClick={() => setSelectedAgent(key)}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors ${
                  selectedAgent === key
                    ? "bg-primary-500/10 text-primary-600 font-medium"
                    : "text-text-secondary hover:bg-neutral-bg"
                }`}
              >
                <Icon size={18} className={selectedAgent === key ? "text-primary-500" : color} />
                <div className="min-w-0 flex-1">
                  <p className="truncate">{label}</p>
                  <p className="text-[10px] text-text-tertiary">
                    {status?.status === "ready" ? "Ready" : "Needs API key"}
                  </p>
                </div>
                {selectedAgent === key && (
                  <span className="h-2 w-2 rounded-full bg-primary-500" />
                )}
              </button>
            );
          })}
        </div>

        <div className="border-t border-neutral-bg pt-3">
          <h3 className="px-1 text-xs font-semibold text-text-tertiary">Quick Actions</h3>
          <div className="mt-2 space-y-1">
            {[
              { label: "Analyze a prospect", agent: "prospect", msg: "Analyze Infosys Technologies as a prospect. Revenue ₹1.47L Cr, 314k employees, IT Services, Karnataka." },
              { label: "Check deal risk", agent: "deal_intel", msg: "Assess risk for a ₹12Cr deal with HDFC Bank in Proposal stage, 8 days in stage, 2 competitor mentions." },
              { label: "Generate battlecard", agent: "competitive", msg: "Generate a battlecard comparing SalesEdge vs Salesforce for Indian BFSI enterprise deals." },
            ].map((qa) => (
              <button
                key={qa.label}
                onClick={() => {
                  setSelectedAgent(qa.agent);
                  setInput(qa.msg);
                }}
                className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-xs text-text-tertiary hover:bg-neutral-bg hover:text-text-secondary transition-colors"
              >
                <Sparkles size={12} className="shrink-0 text-primary-400" />
                {qa.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex flex-1 flex-col overflow-hidden rounded-lg border border-neutral-bg bg-surface-card">
        {/* Chat Header */}
        <div className="flex items-center gap-3 border-b border-neutral-bg px-4 py-3">
          <AgentIcon size={20} className={meta.color} />
          <div>
            <p className="text-sm font-semibold text-text-primary">{meta.label}</p>
            <p className="text-xs text-text-tertiary">
              {agents.find((a) => a.name === `${selectedAgent}_agent`)?.description ?? "AI-powered analysis"}
            </p>
          </div>
          {chatMutation.isPending && (
            <Loader2 size={16} className="ml-auto animate-spin text-primary-500" />
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <Bot size={48} className="text-neutral/30" />
              <p className="mt-4 text-sm font-medium text-text-secondary">
                Start a conversation with {meta.label}
              </p>
              <p className="mt-1 max-w-sm text-xs text-text-tertiary">
                Ask questions about prospects, deals, retention risks, or competitors.
                The agent uses real-time data from your pipeline and market signals.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm ${
                  msg.role === "user"
                    ? "bg-primary-500 text-white"
                    : "bg-neutral-bg text-text-primary"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                <p className={`mt-1 text-[10px] ${msg.role === "user" ? "text-white/60" : "text-text-tertiary"}`}>
                  {new Date(msg.timestamp).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
            </div>
          ))}

          {chatMutation.isPending && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-xl bg-neutral-bg px-4 py-3">
                <Loader2 size={14} className="animate-spin text-primary-500" />
                <span className="text-xs text-text-tertiary">Thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-neutral-bg p-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder={meta.placeholder}
              disabled={chatMutation.isPending}
              className="flex-1 rounded-lg border border-neutral-bg bg-surface-background px-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-primary-300 focus:outline-none disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || chatMutation.isPending}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-500 text-white transition-colors hover:bg-primary-600 disabled:opacity-40"
            >
              <Send size={16} />
            </button>
          </div>
          {!isLLMConfigured && (
            <p className="mt-2 flex items-center gap-1 text-[11px] text-caution">
              <AlertTriangle size={12} />
              Agents require an LLM API key. Configure in Settings.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
