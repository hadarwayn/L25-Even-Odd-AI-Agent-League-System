"""
Player Agent - Entry point.

Participates in Even/Odd games using configurable strategies.
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add SHARED to path for league_sdk imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

import uvicorn
from league_sdk import MCPServer, MCPClient, JsonLogger, get_config

from handlers import PlayerHandlers
from state import PlayerState
from strategies import get_strategy


class PlayerAgent:
    """Player agent that participates in games."""

    def __init__(
        self,
        player_id: str,
        port: int,
        display_name: str = "",
        strategy_name: str = "random",
    ):
        """
        Initialize Player agent.

        Args:
            player_id: Player identifier (e.g., "P01")
            port: Server port
            display_name: Display name for the player
            strategy_name: Strategy to use
        """
        self.player_id = player_id
        self.display_name = display_name or f"Player_{player_id}"
        self.config = get_config()

        self.host = "127.0.0.1"
        self.port = port

        self.server = MCPServer("player", player_id, self.host, port)
        self.logger = JsonLogger("players", player_id)

        # State and strategy
        self.state = PlayerState(player_id)
        self.strategy = get_strategy(strategy_name)

        # Handlers
        self.handlers = PlayerHandlers(self)
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register message handlers."""
        self.server.register_handler(
            "GAME_INVITATION",
            self.handlers.handle_game_invitation,
        )
        self.server.register_handler(
            "CHOOSE_PARITY_CALL",
            self.handlers.handle_choose_parity,
        )
        self.server.register_handler(
            "GAME_OVER",
            self.handlers.handle_game_over,
        )
        self.server.register_handler(
            "ROUND_ANNOUNCEMENT",
            self.handlers.handle_round_announcement,
        )
        self.server.register_handler(
            "LEAGUE_STANDINGS_UPDATE",
            self.handlers.handle_standings_update,
        )
        self.server.register_handler(
            "LEAGUE_COMPLETED",
            self.handlers.handle_league_completed,
        )

    async def register_with_manager(self) -> bool:
        """Register with League Manager."""
        manager_endpoint = self.config.agents.get("league_manager", {}).get(
            "endpoint", "http://127.0.0.1:8000/mcp"
        )

        client = MCPClient(f"player:{self.player_id}")

        try:
            response = await client.send(
                manager_endpoint,
                "LEAGUE_REGISTER_REQUEST",
                {
                    "player_meta": {
                        "display_name": self.display_name,
                        "version": "1.0.0",
                        "protocol_version": "league.v2",
                        "game_types": ["even_odd"],
                        "contact_endpoint": f"http://{self.host}:{self.port}/mcp",
                    }
                },
            )

            result = response.get("result", {})
            if result.get("status") == "REGISTERED":
                assigned_id = result.get("player_id", self.player_id)
                self.state.set_registered(assigned_id, result.get("auth_token", ""))
                self.logger.info("REGISTERED", f"Registered as {assigned_id}")
                return True

        except Exception as e:
            self.logger.error("REGISTRATION_FAILED", str(e))

        await client.close()
        return False

    def run(self) -> None:
        """Run the Player server."""
        print("=" * 60)
        print("    Even/Odd League Player Agent")
        print("=" * 60)
        print(f"  Player ID:     {self.player_id}")
        print(f"  Display Name:  {self.display_name}")
        print(f"  Port:          {self.port}")
        print(f"  Strategy:      {self.strategy.name}")
        print(f"  Endpoint:      http://{self.host}:{self.port}/mcp")
        print("=" * 60)

        self.logger.info("STARTUP", f"Player {self.player_id} starting")

        # Schedule registration
        @self.server.app.on_event("startup")
        async def startup():
            await self.register_with_manager()

        uvicorn.run(self.server.app, host=self.host, port=self.port)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="Player Agent")
    parser.add_argument("--id", default="P01", help="Player ID")
    parser.add_argument("--port", type=int, default=8101, help="Server port")
    parser.add_argument("--name", default="", help="Display name")
    parser.add_argument("--strategy", default="random", help="Strategy name")
    args = parser.parse_args()

    player = PlayerAgent(args.id, args.port, args.name, args.strategy)
    player.run()


if __name__ == "__main__":
    main()
