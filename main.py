#!/usr/bin/env python3
"""
Even/Odd League Player Agent - Main Entry Point

This script starts the Player Agent:
1. Loads configuration from config/settings.yaml and environment
2. Initializes player state
3. Starts the FastAPI MCP server
4. Registers with the League Manager
5. Handles incoming game invitations and plays matches

Usage:
    python main.py
    python main.py --port 8102
    python main.py --name "MyAgent"
"""

import sys
import asyncio
import argparse
from pathlib import Path

import uvicorn

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import load_config, get_contact_endpoint
from src.utils.logger import setup_logger
from src.agents.player_agent.state import PlayerState
from src.agents.player_agent.handlers import MessageHandler
from src.agents.player_agent.server import create_app
from src.agents.player_agent.registration import register_with_league, RegistrationError
from src.strategy.random_strategy import RandomStrategy


async def register_on_startup(config, state, logger):
    """Register with League Manager after server starts."""
    await asyncio.sleep(1)  # Wait for server to be ready

    try:
        await register_with_league(config, state, logger)
    except RegistrationError as e:
        logger.error("STARTUP_ERROR", f"Registration failed: {e}")
        print(f"ERROR: Registration failed: {e}")
    except Exception as e:
        logger.error("STARTUP_ERROR", f"Unexpected error during registration: {e}")
        print(f"ERROR: Registration error: {e}")


def main():
    """Main entry point for the Player Agent."""
    parser = argparse.ArgumentParser(
        description="Even/Odd League Player Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run the server on (default: from config)",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Display name for the agent (default: from config)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/settings.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Skip automatic registration (for testing)",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Override with command line arguments
    if args.port:
        config.server.port = args.port
    if args.name:
        config.agent.display_name = args.name

    # Initialize logger with a temporary ID until registration
    temp_id = f"agent_{config.server.port}"
    logger = setup_logger(
        player_id=temp_id,
        log_dir=config.logging.directory,
        level=config.logging.level,
    )

    # Initialize player state
    state = PlayerState()
    state.set_data_dir(config.data.players_directory)

    # Initialize strategy
    strategy = RandomStrategy()

    # Initialize message handler
    handler = MessageHandler(state=state, strategy=strategy, logger=logger)

    # Create FastAPI app
    app = create_app(state=state, handler=handler, logger=logger)

    # Print startup info
    print("=" * 60)
    print("    Even/Odd League Player Agent")
    print("=" * 60)
    print(f"  Display Name:    {config.agent.display_name}")
    print(f"  Server Port:     {config.server.port}")
    print(f"  Contact URL:     {get_contact_endpoint(config)}")
    print(f"  League Manager:  {config.league_manager.endpoint}")
    print(f"  Strategy:        {strategy.get_name()}")
    print("=" * 60)

    logger.info(
        "AGENT_STARTING",
        f"Starting player agent on port {config.server.port}",
        display_name=config.agent.display_name,
    )

    # Schedule registration after startup
    if not args.no_register:
        @app.on_event("startup")
        async def startup_registration():
            asyncio.create_task(register_on_startup(config, state, logger))

    # Run server
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
