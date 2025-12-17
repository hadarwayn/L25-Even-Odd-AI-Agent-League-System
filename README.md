# Even/Odd AI Agent League System

A distributed multi-agent system implementing a competitive Even/Odd game league. The system includes three agent types (League Manager, Referee, Player) that communicate via the `league.v2` protocol using MCP (Model Context Protocol) over JSON-RPC 2.0 HTTP transport.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  LEAGUE MANAGEMENT LAYER                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │           League Manager (Port 8000)             │   │
│  │  - Player/Referee registration                   │   │
│  │  - Round-robin scheduling                        │   │
│  │  - Standings calculation                         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                  GAME REFEREEING LAYER                   │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  Referee REF01   │    │  Referee REF02   │          │
│  │  (Port 8001)     │    │  (Port 8002)     │          │
│  └──────────────────┘    └──────────────────┘          │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                    PLAYER LAYER                          │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │
│  │  P01   │ │  P02   │ │  P03   │ │  P04   │          │
│  │ :8101  │ │ :8102  │ │ :8103  │ │ :8104  │          │
│  └────────┘ └────────┘ └────────┘ └────────┘          │
└─────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Agent Architecture**: League Manager, Referees, and Players
- **Protocol Compliance**: Full `league.v2` protocol with 18 message types
- **Pluggable Strategies**: Random, Deterministic, Alternating, Adaptive
- **Shared SDK**: Common components in `SHARED/league_sdk/`
- **JSONL Logging**: Structured logging for all agents
- **State Persistence**: Agents survive restarts
- **Visualization**: Performance graphs and charts

## Virtual Environment Setup (REQUIRED)

This project uses **UV** for fast, reliable package management.

### Step 1: Install UV (if not installed)

**Linux/Mac/WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows PowerShell:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Create and Activate Virtual Environment

```bash
cd L25
uv venv
```

**WSL/Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
uv pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python --version
# Should show Python 3.10+

python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
```

## Running the Full League

Start agents in separate terminals in this order:

### Terminal 1: League Manager
```bash
cd agents/league_manager && python main.py
```

### Terminal 2: Referee REF01
```bash
cd agents/referee_REF01 && python main.py
```

### Terminal 3: Referee REF02
```bash
cd agents/referee_REF02 && python main.py
```

### Terminal 4: Player P01 (AlphaBot - Random)
```bash
cd agents/player_P01 && python main.py
```

### Terminal 5: Player P02 (BetaBot - Deterministic Even)
```bash
cd agents/player_P02 && python main.py
```

### Terminal 6: Player P03 (GammaBot - Alternating)
```bash
cd agents/player_P03 && python main.py
```

### Terminal 7: Player P04 (DeltaBot - Adaptive)
```bash
cd agents/player_P04 && python main.py
```

## Player Strategies

| Player | Strategy | Description |
|--------|----------|-------------|
| P01 | Random | Equal probability even/odd |
| P02 | Deterministic Even | Always chooses even |
| P03 | Alternating | Switches between even/odd |
| P04 | Adaptive | Learns from opponent history |

## Project Structure

```
L25/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── SHARED/                      # Shared SDK and resources
│   ├── config/
│   │   ├── system.json          # Protocol settings
│   │   ├── agents.json          # Agent definitions
│   │   └── league.json          # League settings
│   ├── data/
│   │   ├── standings/           # League standings
│   │   ├── matches/             # Match history
│   │   └── state/               # Agent state persistence
│   ├── logs/
│   │   ├── league_manager/
│   │   ├── referees/
│   │   └── players/
│   └── league_sdk/              # Python SDK package
│       ├── __init__.py
│       ├── config_loader.py
│       ├── config_models.py
│       ├── schemas.py           # All 18 message types
│       ├── mcp_client.py
│       ├── mcp_server.py
│       ├── repositories.py
│       ├── logger.py
│       ├── helpers.py
│       └── game_rules/
│           └── even_odd.py
│
├── agents/
│   ├── league_manager/
│   │   ├── main.py
│   │   ├── handlers.py
│   │   ├── scheduler.py
│   │   └── standings.py
│   ├── referee_template/
│   │   ├── main.py
│   │   ├── handlers.py
│   │   └── game_logic.py
│   ├── referee_REF01/
│   ├── referee_REF02/
│   ├── player_template/
│   │   ├── main.py
│   │   ├── handlers.py
│   │   ├── state.py
│   │   └── strategies/
│   │       ├── base.py
│   │       ├── random_strategy.py
│   │       ├── deterministic.py
│   │       ├── alternating.py
│   │       └── adaptive.py
│   ├── player_P01/
│   ├── player_P02/
│   ├── player_P03/
│   └── player_P04/
│
├── src/                         # Original player agent code
│   └── visualizer.py
│
├── results/
│   ├── graphs/
│   └── examples/
│
├── docs/
│   ├── PRD.md
│   └── tasks.json
│
└── tests/
    ├── test_protocol.py
    └── test_handlers.py
```

## Protocol Compliance

### Message Types (18 Total)

| Category | Message Type | Direction |
|----------|--------------|-----------|
| Registration | `LEAGUE_REGISTER_REQUEST` | Agent → Manager |
| Registration | `LEAGUE_REGISTER_RESPONSE` | Manager → Agent |
| Registration | `REFEREE_REGISTER_REQUEST` | Referee → Manager |
| Registration | `REFEREE_REGISTER_RESPONSE` | Manager → Referee |
| Round | `ROUND_ANNOUNCEMENT` | Manager → All |
| Round | `ROUND_COMPLETED` | Manager → All |
| Match | `GAME_INVITATION` | Referee → Player |
| Match | `GAME_JOIN_ACK` | Player → Referee |
| Match | `CHOOSE_PARITY_CALL` | Referee → Player |
| Match | `CHOOSE_PARITY_RESPONSE` | Player → Referee |
| Match | `GAME_OVER` | Referee → Player |
| Match | `MATCH_RESULT_REPORT` | Referee → Manager |
| Standings | `LEAGUE_STANDINGS_UPDATE` | Manager → All |
| Query | `LEAGUE_QUERY` | Player → Manager |
| Query | `LEAGUE_QUERY_RESPONSE` | Manager → Player |
| Completion | `LEAGUE_COMPLETED` | Manager → All |
| Error | `LEAGUE_ERROR` | Manager → Agent |
| Error | `GAME_ERROR` | Referee → Player |

### Timeouts

| Operation | Timeout |
|-----------|---------|
| Registration | 10 sec |
| Game Join | 5 sec |
| Parity Choice | 30 sec |
| Match Result Report | 10 sec |

### Scoring

- **Win**: 3 points
- **Draw**: 1 point
- **Loss**: 0 points

## SDK Components

The shared SDK (`SHARED/league_sdk/`) provides:

| Module | Purpose |
|--------|---------|
| `config_loader.py` | Lazy-load JSON configuration with caching |
| `config_models.py` | Type-safe dataclass configuration models |
| `schemas.py` | Complete Pydantic models for all 18 message types |
| `mcp_client.py` | HTTP client with retry logic |
| `mcp_server.py` | Base MCP server class for agents |
| `repositories.py` | Data access (standings, matches, state) |
| `logger.py` | JSONL structured logging |
| `helpers.py` | UTC timestamps, ID generation, validation |
| `game_rules/even_odd.py` | Even/Odd game logic |

## API Endpoints

All agents expose:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | Main MCP protocol endpoint |
| `/health` | GET | Health check |

## Quick Simulation

Run a complete league simulation in a single command:

```bash
python run_league.py
```

## Results

### League Activity Log

| Time | Event | Details |
|------|-------|---------|
| 11:04:29 | REFEREE_REGISTERED | REF01 registered |
| 11:04:29 | REFEREE_REGISTERED | REF02 registered |
| 11:04:29 | PLAYER_REGISTERED | P01 (AlphaBot) registered |
| 11:04:29 | PLAYER_REGISTERED | P02 (BetaBot) registered |
| 11:04:29 | PLAYER_REGISTERED | P03 (GammaBot) registered |
| 11:04:29 | PLAYER_REGISTERED | P04 (DeltaBot) registered |
| 11:04:29 | SCHEDULE_GENERATED | 3 rounds, 6 matches |
| 11:04:29 | LEAGUE_START | League starting |
| 11:04:29 | ROUND_START | Round 1 starting |
| 11:04:29 | MATCH_COMPLETED | R1M1: P01 vs P02 -> DRAW |
| 11:04:29 | MATCH_COMPLETED | R1M2: P03 vs P04 -> DRAW |
| 11:04:29 | ROUND_COMPLETED | Round 1 completed |
| 11:04:29 | ROUND_START | Round 2 starting |
| 11:04:29 | MATCH_COMPLETED | R2M1: P01 vs P03 -> DRAW |
| 11:04:29 | MATCH_COMPLETED | R2M2: P02 vs P04 -> DRAW |
| 11:04:29 | ROUND_COMPLETED | Round 2 completed |
| 11:04:29 | ROUND_START | Round 3 starting |
| 11:04:29 | MATCH_COMPLETED | R3M1: P01 vs P04 -> P04 |
| 11:04:29 | MATCH_COMPLETED | R3M2: P02 vs P03 -> DRAW |
| 11:04:29 | ROUND_COMPLETED | Round 3 completed |
| 11:04:29 | LEAGUE_COMPLETED | League finished |

### Match History

| Match | Round | Player A | Choice | vs | Player B | Choice | Draw# | Winner |
|-------|-------|----------|--------|-----|----------|--------|-------|--------|
| R1M1 | 1 | P01 | even | vs | P02 | even | 5 | DRAW |
| R1M2 | 1 | P03 | even | vs | P04 | even | 6 | DRAW |
| R2M1 | 2 | P01 | odd | vs | P03 | odd | 10 | DRAW |
| R2M2 | 2 | P02 | even | vs | P04 | even | 1 | DRAW |
| R3M1 | 3 | P01 | even | vs | P04 | odd | 1 | P04 |
| R3M2 | 3 | P02 | even | vs | P03 | even | 8 | DRAW |

### Final Standings

| Rank | Player | Strategy | P | W | D | L | Pts |
|------|--------|----------|---|---|---|---|-----|
| 1 | P04 (DeltaBot) | adaptive | 3 | 1 | 2 | 0 | 5 |
| 2 | P02 (BetaBot) | deterministic_even | 3 | 0 | 3 | 0 | 3 |
| 3 | P03 (GammaBot) | alternating | 3 | 0 | 3 | 0 | 3 |
| 4 | P01 (AlphaBot) | random | 3 | 0 | 2 | 1 | 2 |

### Champion

**P04 (DeltaBot)** - Adaptive Strategy
- Record: 1W-2D-0L (5 points)
- The adaptive strategy won by learning opponent patterns!

## Visualization

Generate visualizations after running games:

```bash
python src/visualizer.py
```

Output in `results/graphs/`:
- `results_distribution.png` - Win/loss/draw pie chart
- `performance_timeline.png` - Points over time
- `choice_analysis.png` - Even vs odd effectiveness

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

## Troubleshooting

### "Module not found" error
Ensure virtual environment is activated:
```bash
source .venv/bin/activate  # Linux/Mac/WSL
.venv\Scripts\activate     # Windows
```

### Connection refused
Start agents in order: Manager → Referees → Players

### Registration timeout
Check League Manager is running:
```bash
curl http://localhost:8000/health
```

## Learning Objectives

This project demonstrates:
1. **Multi-Agent Systems** - Coordination between autonomous agents
2. **MCP Protocol** - JSON-RPC 2.0 over HTTP implementation
3. **Distributed Architecture** - Three-layer system design
4. **Protocol Compliance** - Strict specification adherence
5. **Strategy Pattern** - Pluggable decision algorithms
6. **Repository Pattern** - Clean data access abstraction

## License

Open source for educational use.
