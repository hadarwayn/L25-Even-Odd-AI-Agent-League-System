"""
Referee Agent - Entry point.

Orchestrates matches between players.
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add SHARED to path for league_sdk imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

import uvicorn
from league_sdk import MCPServer, MCPClient, JsonLogger, get_config

from handlers import RefereeHandlers
from game_logic import GameOrchestrator


class RefereeAgent:
    """Referee agent that orchestrates matches."""

    def __init__(self, referee_id: str, port: int):
        """
        Initialize Referee agent.

        Args:
            referee_id: Referee identifier (e.g., "REF01")
            port: Server port
        """
        self.referee_id = referee_id
        self.config = get_config()

        self.host = "127.0.0.1"
        self.port = port

        self.server = MCPServer("referee", referee_id, self.host, port)
        self.logger = JsonLogger("referees", referee_id)

        # State
        self.auth_token: str = ""
        self.registered = False
        self.active_matches: dict[str, dict] = {}

        # Components
        self.orchestrator = GameOrchestrator(self)
        self.handlers = RefereeHandlers(self)
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register message handlers."""
        self.server.register_handler(
            "GAME_JOIN_ACK",
            self.handlers.handle_game_join_ack,
        )
        self.server.register_handler(
            "CHOOSE_PARITY_RESPONSE",
            self.handlers.handle_parity_response,
        )

    async def register_with_manager(self) -> bool:
        """Register with League Manager."""
        manager_endpoint = self.config.agents.get("league_manager", {}).get(
            "endpoint", "http://127.0.0.1:8000/mcp"
        )

        client = MCPClient(f"referee:{self.referee_id}")

        try:
            response = await client.send(
                manager_endpoint,
                "REFEREE_REGISTER_REQUEST",
                {
                    "referee_meta": {
                        "version": "1.0.0",
                        "protocol_version": "league.v2",
                        "contact_endpoint": f"http://{self.host}:{self.port}/mcp",
                    }
                },
            )

            result = response.get("result", {})
            if result.get("status") == "REGISTERED":
                self.auth_token = result.get("auth_token", "")
                self.registered = True
                self.logger.info(
                    "REGISTERED",
                    f"Registered as {result.get('referee_id')}",
                )
                return True

        except Exception as e:
            self.logger.error("REGISTRATION_FAILED", str(e))

        await client.close()
        return False

    def run(self) -> None:
        """Run the Referee server."""
        print("=" * 60)
        print("    Even/Odd League Referee")
        print("=" * 60)
        print(f"  Referee ID:    {self.referee_id}")
        print(f"  Port:          {self.port}")
        print(f"  Endpoint:      http://{self.host}:{self.port}/mcp")
        print("=" * 60)

        self.logger.info("STARTUP", f"Referee {self.referee_id} starting")

        # Schedule registration
        @self.server.app.on_event("startup")
        async def startup():
            await self.register_with_manager()

        uvicorn.run(self.server.app, host=self.host, port=self.port)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="Referee Agent")
    parser.add_argument("--id", default="REF01", help="Referee ID")
    parser.add_argument("--port", type=int, default=8001, help="Server port")
    args = parser.parse_args()

    referee = RefereeAgent(args.id, args.port)
    referee.run()


if __name__ == "__main__":
    main()
