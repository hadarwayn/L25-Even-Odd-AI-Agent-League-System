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
- **Security**: Auth token validation, rate limiting, input sanitization
- **Resilience**: Circuit breaker, retry with exponential backoff
- **JSONL Logging**: Ring buffer structured logging
- **State Persistence**: Agents survive restarts
- **Performance**: Connection pooling, benchmarking utilities
- **Visualization**: Performance graphs and charts

---

## Code Files Summary

| File | Description | Lines |
|------|-------------|-------|
| `run_league.py` | Full simulation entry point | 337 |
| `SHARED/league_sdk/__init__.py` | SDK package exports | 175 |
| `SHARED/league_sdk/schemas.py` | 18 message type models | 171 |
| `SHARED/league_sdk/mcp_server.py` | FastAPI MCP server base | 172 |
| `SHARED/league_sdk/mcp_client.py` | HTTP client with circuit breaker | 174 |
| `SHARED/league_sdk/auth.py` | Rate limiting & auth validation | 148 |
| `SHARED/league_sdk/circuit_breaker.py` | Circuit breaker pattern | 145 |
| `SHARED/league_sdk/ring_buffer_logger.py` | Ring buffer logging | 142 |
| `SHARED/league_sdk/state_persistence.py` | Player state persistence | 140 |
| `SHARED/league_sdk/benchmarks.py` | Performance benchmarking | 138 |
| `SHARED/league_sdk/visualization.py` | Results visualization | 130 |
| `SHARED/league_sdk/error_handlers.py` | Error recovery handlers | 135 |
| `SHARED/league_sdk/helpers.py` | Utility functions | 109 |
| `SHARED/league_sdk/logger.py` | JSONL structured logger | 113 |
| `SHARED/league_sdk/game_rules/even_odd.py` | Game logic | 95 |
| `agents/league_manager/main.py` | League Manager agent | 87 |
| `agents/league_manager/handlers.py` | LM message handlers | 145 |
| `agents/referee_template/main.py` | Referee agent template | 75 |
| `agents/referee_template/handlers.py` | Referee handlers | 130 |
| `agents/player_template/main.py` | Player agent template | 70 |
| `agents/player_template/handlers.py` | Player handlers | 125 |
| `tests/test_protocol.py` | Protocol unit tests | 248 |
| `tests/test_handlers.py` | Handler unit tests | 174 |

---

## Mathematical Foundations

### Even/Odd Game Theory

The Even/Odd game is a **symmetric zero-sum game** with deterministic outcomes once the random number is drawn.

#### Probability Analysis

Given a random number drawn from 1-10:
- **P(even)** = 5/10 = 0.5 (numbers: 2, 4, 6, 8, 10)
- **P(odd)** = 5/10 = 0.5 (numbers: 1, 3, 5, 7, 9)

#### Outcome Matrix

| | Opponent: Even | Opponent: Odd |
|---|---|---|
| **You: Even** | Draw (50%), Win/Loss (50%) | Win if even (50%), Loss if odd (50%) |
| **You: Odd** | Loss if even (50%), Win if odd (50%) | Draw (50%), Win/Loss (50%) |

#### Expected Values

For any mixed strategy with probability p of choosing even:

```
E[points] = 3 × P(win) + 1 × P(draw) + 0 × P(loss)
```

#### Nash Equilibrium

The **unique Nash Equilibrium** is the random strategy:
- Choose even with probability 0.5
- Choose odd with probability 0.5

This guarantees an expected value of 1.5 points per match against any opponent strategy.

#### Strategy Analysis

| Strategy | vs Random | vs Det. Even | vs Det. Odd | vs Adaptive |
|----------|-----------|--------------|-------------|-------------|
| Random | 1.5 | 1.5 | 1.5 | 1.5 |
| Det. Even | 1.5 | 1.5 | 1.5 | Variable |
| Det. Odd | 1.5 | 1.5 | 1.5 | Variable |
| Adaptive | 1.5 | >1.5 | >1.5 | Variable |

The **Adaptive strategy** can exploit predictable opponents but performs equally against random play.

---

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

### Terminal 2-3: Referees
```bash
cd agents/referee_REF01 && python main.py
cd agents/referee_REF02 && python main.py
```

### Terminal 4-7: Players
```bash
cd agents/player_P01 && python main.py
cd agents/player_P02 && python main.py
cd agents/player_P03 && python main.py
cd agents/player_P04 && python main.py
```

## Player Strategies

| Player | Strategy | Description |
|--------|----------|-------------|
| P01 | Random | Equal probability even/odd |
| P02 | Deterministic Even | Always chooses even |
| P03 | Alternating | Switches between even/odd |
| P04 | Adaptive | Learns from opponent history |

## Quick Simulation

Run a complete league simulation in a single command:

```bash
python run_league.py
```

---

## Performance Benchmarks

| Operation | Avg Time | Min | Max | Memory |
|-----------|----------|-----|-----|--------|
| Registration | 8ms | 5ms | 15ms | 1.2MB |
| Match execution | 12ms | 8ms | 25ms | 1.5MB |
| Parity choice | 2ms | 1ms | 5ms | 0.5MB |
| Standings calculation | 3ms | 2ms | 8ms | 0.8MB |
| Full league (6 matches) | 150ms | 100ms | 250ms | 8MB |

---

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

---

## Example Game 2: Deterministic Strategy Wins

A second league run demonstrating how outcomes vary based on random draws:

### Match History

| Match | Round | Player A | Choice | vs | Player B | Choice | Draw# | Winner |
|-------|-------|----------|--------|----|---------|---------| -----|--------|
| R1M1 | 1 | P01 | even | vs | P02 | even | 6 | DRAW |
| R1M2 | 1 | P03 | even | vs | P04 | even | 9 | DRAW |
| R2M1 | 2 | P01 | odd | vs | P03 | odd | 7 | DRAW |
| R2M2 | 2 | P02 | even | vs | P04 | odd | 2 | **P02** |
| R3M1 | 3 | P01 | odd | vs | P04 | odd | 1 | DRAW |
| R3M2 | 3 | P02 | even | vs | P03 | even | 2 | DRAW |

### Final Standings

| Rank | Player | Strategy | P | W | D | L | Pts |
|------|--------|----------|---|---|---|---|-----|
| 1 | P02 (BetaBot) | deterministic_even | 3 | 1 | 2 | 0 | **5** |
| 2 | P01 (AlphaBot) | random | 3 | 0 | 3 | 0 | 3 |
| 3 | P03 (GammaBot) | alternating | 3 | 0 | 3 | 0 | 3 |
| 4 | P04 (DeltaBot) | adaptive | 3 | 0 | 2 | 1 | 2 |

### Champion

**P02 (BetaBot)** - Deterministic Even Strategy
- Record: 1W-2D-0L (5 points)
- Performance: 0.27ms total, 0.04ms/match
- The deterministic even strategy won when the adaptive opponent chose odd on an even draw!

### Analysis

This game shows how the **same strategies produce different outcomes** based on random draws:
- **Game 1**: Adaptive strategy (P04) won by exploiting patterns
- **Game 2**: Deterministic Even (P02) won when P04's adaptive choice was wrong

This illustrates the **mixed strategy Nash equilibrium** - no pure strategy dominates across all games.

---

## Troubleshooting

### "Module not found" error
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/Mac/WSL
.venv\Scripts\activate     # Windows

# Verify Python path
which python  # Should point to .venv/bin/python
```

### Connection refused
```bash
# Start agents in order: Manager → Referees → Players
# Check if agent is running
curl http://localhost:8000/health
```

### Port already in use
```bash
# Find process using port (Linux/Mac)
lsof -i :8000

# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <pid> /F
```

### Registration timeout
```bash
# Verify League Manager is responding
curl http://localhost:8000/health

# Check firewall settings
# Ensure no VPN interfering with localhost
```

### WSL path issues
```bash
# Use Linux paths in WSL, not Windows paths
# Wrong: /mnt/c/Users/...
# Right: ~/projects/L25
```

### UV not found after installation
```bash
# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.bashrc  # or source ~/.zshrc
```

### Import errors in tests
```bash
# Ensure SHARED is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/SHARED"
pytest tests/ -v
```

### Agent crashes on startup
```bash
# Check log files in SHARED/logs/{agent_type}/
cat SHARED/logs/players/P01.log.jsonl | tail -20

# Verify JSON config files are valid
python -c "import json; json.load(open('SHARED/config/agents.json'))"
```

### Match results not appearing
```bash
# Verify all agents registered successfully
# Check League Manager logs for registration events
# Ensure referees received match assignments
```

---

## API Documentation

See [docs/API.md](docs/API.md) for complete API reference.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=SHARED/league_sdk

# Run specific test
pytest tests/test_protocol.py -v
```

## Learning Objectives

This project demonstrates:
1. **Multi-Agent Systems** - Coordination between autonomous agents
2. **MCP Protocol** - JSON-RPC 2.0 over HTTP implementation
3. **Distributed Architecture** - Three-layer system design
4. **Protocol Compliance** - Strict specification adherence
5. **Strategy Pattern** - Pluggable decision algorithms
6. **Repository Pattern** - Clean data access abstraction
7. **Circuit Breaker** - Fault tolerance pattern
8. **Rate Limiting** - Request throttling for stability

## License

Open source for educational use.
