"""Abstract base agent and shared data structures for all SalesEdge agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import uuid4


class ActionType(str, Enum):
    NOTIFY = "notify"
    CREATE_TASK = "create_task"
    UPDATE_DEAL = "update_deal"
    TRIGGER_OUTREACH = "trigger_outreach"
    ESCALATE = "escalate"
    UPDATE_RECORD = "update_record"
    GENERATE_REPORT = "generate_report"


@dataclass
class AgentContext:
    """Shared context passed to every agent execution cycle."""

    run_id: str = field(default_factory=lambda: uuid4().hex)
    triggered_by: str = "scheduler"
    entity_id: str | None = None
    entity_type: str | None = None
    signal_payload: dict[str, Any] = field(default_factory=dict)
    user_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentAction:
    """An action that an agent recommends or requests execution of."""

    action_id: str = field(default_factory=lambda: uuid4().hex)
    action_type: ActionType = ActionType.NOTIFY
    target_entity_id: str | None = None
    target_entity_type: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    rationale: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentResult:
    """Outcome of an agent execution cycle."""

    agent_name: str
    run_id: str
    success: bool
    actions: list[AgentAction] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0.0
    completed_at: datetime = field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """Abstract base class for all SalesEdge autonomous agents.

    Subclasses must implement ``execute`` (main logic) and ``get_actions``
    (what the agent can do given the current context).
    """

    name: str = "base_agent"
    description: str = ""
    status: Literal["idle", "active", "error"] = "idle"
    last_run: datetime | None = None
    _run_count: int = 0

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Run the agent's main logic and return a result with any actions."""
        ...

    @abstractmethod
    async def get_actions(self, context: AgentContext) -> list[AgentAction]:
        """Return the set of actions the agent would take given the context,
        without actually executing them (dry-run / preview)."""
        ...

    async def _run_with_lifecycle(self, context: AgentContext) -> AgentResult:
        """Wrap ``execute`` with status tracking and error handling."""
        self.status = "active"
        self._run_count += 1
        start = datetime.utcnow()

        try:
            result = await self.execute(context)
            self.status = "idle"
        except Exception as exc:
            self.status = "error"
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            result = AgentResult(
                agent_name=self.name,
                run_id=context.run_id,
                success=False,
                error=str(exc),
                duration_ms=elapsed,
            )

        self.last_run = datetime.utcnow()
        return result

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={self.name!r} "
            f"status={self.status!r} runs={self._run_count}>"
        )
