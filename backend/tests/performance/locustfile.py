"""Locust load test definitions for SalesEdge API.

Usage:
    locust -f backend/tests/performance/locustfile.py --host http://localhost:8000

Web UI will be available at http://localhost:8089
"""

from __future__ import annotations

from locust import HttpUser, between, task


class SalesEdgeUser(HttpUser):
    """Simulates a sales rep browsing the SalesEdge platform."""

    wait_time = between(1, 3)
    auth_token: str | None = None

    def on_start(self):
        """Register and login to get an auth token."""
        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": f"loadtest_{self.greenlet.minimal_ident}@test.com",
                "password": "LoadTest123!",
                "full_name": "Load Tester",
            },
        )
        resp = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": f"loadtest_{self.greenlet.minimal_ident}@test.com",
                "password": "LoadTest123!",
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            self.auth_token = data.get("access_token") or data.get("token")

    @property
    def _headers(self) -> dict[str, str]:
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    @task(5)
    def view_dashboard(self):
        """Most common action: loading the dashboard."""
        self.client.get("/api/v1/dashboard/kpis", headers=self._headers)

    @task(3)
    def browse_prospects(self):
        self.client.get(
            "/api/v1/prospects",
            params={"page": 1, "per_page": 20},
            headers=self._headers,
        )

    @task(3)
    def browse_deals(self):
        self.client.get("/api/v1/deals", headers=self._headers)

    @task(2)
    def view_retention(self):
        self.client.get("/api/v1/retention/overview", headers=self._headers)

    @task(2)
    def view_signals(self):
        self.client.get("/api/v1/signals", headers=self._headers)

    @task(1)
    def view_competitive(self):
        self.client.get("/api/v1/competitive/overview", headers=self._headers)

    @task(1)
    def check_data_provenance(self):
        self.client.get("/api/v1/data-provenance/sources", headers=self._headers)

    @task(1)
    def health_check(self):
        self.client.get("/api/v1/health")


class AgentUser(HttpUser):
    """Simulates users interacting with AI agents (lower frequency)."""

    wait_time = between(5, 15)
    auth_token: str | None = None

    def on_start(self):
        resp = self.client.post(
            "/api/v1/auth/login",
            json={"email": "loadtest_agent@test.com", "password": "LoadTest123!"},
        )
        if resp.status_code == 200:
            data = resp.json()
            self.auth_token = data.get("access_token") or data.get("token")

    @property
    def _headers(self) -> dict[str, str]:
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    @task
    def chat_with_agent(self):
        self.client.post(
            "/api/v1/agents/chat",
            json={
                "message": "Analyze TCS as a prospect",
                "agent": "prospect",
            },
            headers=self._headers,
            timeout=30,
        )
