# Homework Exercise: Even/Odd League - Part 3: Implementation Guide & Submission Requirements

**Dr. Yoram Segal © 2025**  
**Version 2.0**

---

## Section 5: Implementation Guide

### 5.1 Overall Architecture

#### 5.1.1 Component Diagram

The system has three layers and three agent types:

```
League Manager (Port 8000)
    ↓ ↑
Referee (Port 8001–8010)
    ↓ ↑
Player Agents (Port 8101–8104)
```

Each agent is an MCP server exposing a `/mcp` POST endpoint.

#### 5.1.2 Role of the Orchestrator

The League Manager is the orchestrator. It:

1. Registers all agents
2. Creates the match schedule
3. Coordinates game flow
4. Maintains rankings

---

### 5.2 Simple MCP Server in FastAPI

#### 5.2.1 Basic FastAPI Structure

```python
from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

@app.post("/mcp")
async def mcp_handler(request: Request):
    payload = await request.json()
    
    # payload has: jsonrpc, method, params, id
    method = payload.get("method")
    params = payload.get("params")
    msg_id = payload.get("id")
    
    # Route to handler based on message_type in params
    message_type = params.get("message_type")
    
    if message_type == "GAME_INVITATION":
        result = handle_game_invitation(params)
    elif message_type == "CHOOSE_PARITY_CALL":
        result = handle_choose_parity(params)
    # ... more handlers
    
    response = {
        "jsonrpc": "2.0",
        "result": result,
        "id": msg_id
    }
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8101)
```

---

### 5.3 Player Agent Implementation

#### 5.3.1 Required Tools

- `fastapi`, `uvicorn` – HTTP server
- `pydantic` – Message validation
- `httpx` or `requests` – Client calls
- `python-dotenv` – Config management

#### 5.3.2 Implementation Example

**Agent Startup:**

1. Initialize FastAPI server on port 8101–8104
2. Load config (player name, endpoints)
3. Send `LEAGUE_REGISTER_REQUEST` to Manager on port 8000
4. Wait for response with `player_id` and `auth_token`
5. Store these locally, start accepting game invitations

**Main Handlers:**

```python
def handle_game_invitation(params):
    """Accept game invitation"""
    player_id = params.get("player_id")
    match_id = params.get("match_id")
    # Store match info, prepare for game
    return {"accept": True, "player_id": player_id}

def handle_choose_parity(params):
    """Decide on parity"""
    from strategy import RandomStrategy
    strategy = RandomStrategy()
    choice = strategy.choose()  # "even" or "odd"
    return {"parity_choice": choice}

def handle_game_over(params):
    """Process game result"""
    result = params.get("game_result")
    winner = result.get("winner_player_id")
    drawn_number = result.get("drawn_number")
    # Update local history
    save_match_history(...)
```

---

### 5.4 Referee Implementation

#### 5.4.1 Required Tools

Same as Player Agent

#### 5.4.2 Referee Registration

Before running matches, the Referee must register:

```python
def register_with_manager():
    request = {
        "protocol": "league.v2",
        "message_type": "REFEREE_REGISTER_REQUEST",
        "sender": "referee:UNREGISTERED",
        "timestamp": get_utc_time(),
        "referee_meta": {
            "display_name": "Referee Alpha",
            "supported_games": ["even_odd"],
            "contact_endpoint": "http://localhost:8001/mcp"
        }
    }
    response = call_league_manager(request)
    return response["referee_id"], response["auth_token"]
```

#### 5.4.3 Winner Determination Logic

```python
def determine_winner(choices, drawn_number):
    """choices = {"P01": "even", "P02": "odd"}"""
    is_even = drawn_number % 2 == 0
    parity = "even" if is_even else "odd"
    
    for player_id, choice in choices.items():
        if choice == parity:
            return player_id  # Winner
    
    return None  # Draw
```

---

### 5.5 League Manager Implementation

#### 5.5.1 Required Tools

Same as others

#### 5.5.2 Referee Registration Endpoint

```python
def handle_referee_register(params):
    referee_meta = params.get("referee_meta")
    contact = referee_meta.get("contact_endpoint")
    
    # Assign ID and token
    ref_id = f"REF{len(referees) + 1:02d}"
    token = generate_auth_token()
    
    # Store
    referees[ref_id] = {
        "endpoint": contact,
        "games": referee_meta.get("supported_games")
    }
    
    return {
        "referee_id": ref_id,
        "auth_token": token
    }
```

#### 5.5.3 Create Schedule (Round-Robin)

```python
from itertools import combinations

def create_schedule(players, referees):
    """Create Round-Robin schedule"""
    schedule = []
    round_num = 1
    
    for pair in combinations(players, 2):
        referee = referees[len(schedule) % len(referees)]
        match = {
            "match_id": f"R{round_num}M{len(schedule) + 1}",
            "player_A": pair[0],
            "player_B": pair[1],
            "referee": referee
        }
        schedule.append(match)
    
    return schedule
```

---

### 5.6 Sending HTTP Requests

#### 5.6.1 Calling MCP Tools

```python
import httpx

async def call_mcp_endpoint(endpoint, method, params):
    """Generic MCP call"""
    request_body = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json=request_body,
            timeout=10.0
        )
        return response.json()
```

---

### 5.7 State Management

#### 5.7.1 Player State

```python
class PlayerState:
    def __init__(self):
        self.state = "INIT"  # INIT, REGISTERED, ACTIVE, SUSPENDED, SHUTDOWN
        self.player_id = None
        self.auth_token = None
        self.current_match = None
        self.history = []
    
    def register(self, player_id, auth_token):
        self.player_id = player_id
        self.auth_token = auth_token
        self.state = "REGISTERED"
    
    def start_match(self, match_id):
        self.current_match = match_id
        self.state = "ACTIVE"
    
    def finish_match(self):
        self.current_match = None
        self.state = "REGISTERED"
```

---

### 5.8 Error Handling

#### 5.8.1 Response Timeouts

All handlers must respect timeouts:

- Registration: 10 seconds
- Game Join: 5 seconds
- Parity Choice: 30 seconds

Use async/await to prevent blocking:

```python
import asyncio

async def with_timeout(coro, timeout):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Timeout after {timeout}s")
```

#### 5.8.2 Error Responses

```python
def handle_error(error_code, error_name, description):
    return {
        "message_type": "GAME_ERROR",
        "error_code": error_code,
        "error_name": error_name,
        "error_description": description,
        "retryable": error_code in ["E001", "E009"]
    }
```

---

### 5.9 Resilience Patterns

#### 5.9.1 Retry with Backoff

```python
async def retry_with_backoff(func, max_retries=3, backoff=2):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(backoff)
            else:
                raise
```

#### 5.9.2 Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=60):
        self.failure_count = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func()
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.threshold:
                self.state = "OPEN"
            raise
```

---

### 5.10 Structured Logging

#### 5.10.1 JsonLogger Implementation

```python
import json
from datetime import datetime
import os

class JsonLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def log(self, event_type, **kwargs):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            **kwargs
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
```

#### 5.10.2 Usage Example

```python
logger = JsonLogger("logs/agents/p01.log.jsonl")

logger.log("registration_sent", player_id="P01", endpoint="http://localhost:8000/mcp")
logger.log("game_invitation_received", match_id="R1M1", opponent="P02")
logger.log("parity_choice_made", match_id="R1M1", choice="even")
logger.log("game_over", match_id="R1M1", result="WIN", points=3)
```

---

### 5.11 Authentication & Tokens

#### 5.11.1 Receiving Token on Registration

After `LEAGUE_REGISTER_RESPONSE` with status `"ACCEPTED"`:

```python
def handle_register_response(response):
    if response.get("status") == "ACCEPTED":
        player_id = response.get("player_id")
        auth_token = response.get("auth_token")
        
        state.register(player_id, auth_token)
        save_credentials(player_id, auth_token)
        return True
    else:
        logger.log("registration_failed", reason=response.get("reason"))
        return False
```

#### 5.11.2 Using Token in Requests

Every request after registration must include `auth_token`:

```python
def build_request_with_auth(message_type, params):
    return {
        "protocol": "league.v2",
        "message_type": message_type,
        "sender": f"player:{state.player_id}",
        "timestamp": get_utc_time(),
        "auth_token": state.auth_token,  # Must include!
        **params
    }
```

#### 5.11.3 Handling Auth Errors

```python
if response.get("error_code") == "E011":  # AUTH_TOKEN_MISSING
    logger.log("auth_error", error="token_missing", action="re_register")
    re_register()
elif response.get("error_code") == "E012":  # AUTH_TOKEN_INVALID
    logger.log("auth_error", error="token_invalid", action="shutdown")
    shutdown()
```

---

### 5.12 Local Testing

#### 5.12.1 Running Locally

```bash
# Terminal 1: League Manager
python -m src.league_manager

# Terminal 2: Referee
python -m src.referee

# Terminals 3–6: Players
python -m src.player_agent --port 8101 --name "Agent1"
python -m src.player_agent --port 8102 --name "Agent2"
python -m src.player_agent --port 8103 --name "Agent3"
python -m src.player_agent --port 8104 --name "Agent4"
```

#### 5.12.2 Connection Test

```bash
# Test endpoint connectivity
curl -X POST http://localhost:8101/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","params":{},"id":1}'
```

---

### 5.13 Implementation Tips

1. **Validation First:** Use Pydantic to validate all incoming messages immediately.
2. **Async/Await:** Use FastAPI's async for non-blocking handlers.
3. **Logging:** Log every message sent/received; include timestamps and IDs.
4. **State Persistence:** Save player state to disk so agent can restart without losing identity.
5. **Error Recovery:** Handle timeouts and connection errors gracefully; don't crash.
6. **UTC Timestamps:** Always use UTC; use Python's `datetime.utcnow()` and format with `isoformat() + "Z"`.
7. **Separation of Concerns:** Keep protocol logic, game logic, and server setup in separate modules.

---

## Section 6: Homework Requirements

### 6.1 Exercise Purpose

Build a **Player Agent** that:

1. Registers with a League Manager
2. Plays Even/Odd games via a Referee
3. Follows the `league.v2` protocol strictly
4. Participates in a local private league and (later) a classroom league

---

### 6.2 Mandatory Tasks

#### 6.2.1 Task 1: Implement Player Agent

Create a fully functional Player Agent with:

- **HTTP Server:** FastAPI or equivalent on port 8101–8104
- **Registration Client:** Send `LEAGUE_REGISTER_REQUEST` to Manager on startup
- **Game Handlers:** Accept invitations, choose parity, process results
- **State Management:** Track `player_id`, `auth_token`, match history
- **Strategy:** At minimum, a random choice strategy
- **Logging:** JSON Lines logs to `logs/agents/`
- **History:** Store game outcomes in `data/players/`

#### 6.2.2 Task 2: Register to League

The agent must successfully:

1. Start up an MCP server
2. Send registration request with proper envelope to Manager at port 8000
3. Receive and parse response with `player_id` and `auth_token`
4. Persist identity locally
5. Be ready to accept game invitations

#### 6.2.3 Task 3: Self-Testing

Run your agent in a **private local league** with:

- A reference League Manager (provided or mock)
- A reference Referee (provided or mock)
- At least one full game from invitation to `GAME_OVER`

Document:
- What was tested
- Results (logs, match outcomes)
- Any issues encountered and resolved

---

### 6.3 Technical Requirements

#### 6.3.1 Programming Language

- Python 3.10+ (required)

#### 6.3.2 Response Times

All handlers must meet timeouts:

- Join: ≤ 5 seconds
- Parity: ≤ 30 seconds
- Registration: ≤ 10 seconds

#### 6.3.3 Stability

- Agent must not crash on protocol errors
- Must handle `LEAGUE_ERROR` and `GAME_ERROR` gracefully
- Must handle timeouts and connection failures

---

### 6.4 Workflow

#### 6.4.1 Stage 1: Local Development

1. Set up environment (UV, dependencies)
2. Implement protocol models and server
3. Implement registration and handlers
4. Test with mock endpoints or provided scripts

#### 6.4.2 Stage 2: Private League

1. Deploy agent and reference Manager/Referee locally
2. Run one complete league (all matches)
3. Capture logs and verify correctness
4. Document results

#### 6.4.3 Stage 3: Compatibility with Other Students

1. Test agent against classmates' referees or managers
2. Verify that protocol compliance enables interoperability
3. Note any protocol mismatches and resolve

#### 6.4.4 Future: Classroom League

Once graded and approved, agent can participate in a full classroom league where all students' agents compete.

---

### 6.5 Submission

#### 6.5.1 Files to Submit

1. **Source Code:**
   - `src/agents/player_<name>/` directory with all Python files
   - `src/shared/` (if you use shared utilities)

2. **Configuration:**
   - `config/` directory with sample config files

3. **Documentation:**
   - `PRD.md` – Updated product requirements
   - `tasks.json` – Updated task list with actual hours
   - `README.md` – Setup and run instructions
   - Any additional design docs or architecture diagrams

4. **Data & Logs:**
   - Sample output logs from test runs
   - Sample history files

5. **Version Control:**
   - `.gitignore`, `requirements.txt` (or UV pyproject.toml)
   - Clean, organized repository ready for GitHub

#### 6.5.2 Submission Format

- Prepare as a **GitHub repository** (or ZIP if GitHub not available)
- Include all files above
- Ensure `uv` environment is documented
- Provide clear run instructions in README

---

### 6.6 General Testing Checklist

- [ ] Agent registers and receives `player_id` and `auth_token`
- [ ] Agent accepts `GAME_INVITATION` within 5 seconds
- [ ] Agent responds to `CHOOSE_PARITY_CALL` within 30 seconds
- [ ] Agent receives and logs `GAME_OVER` correctly
- [ ] Agent handles `LEAGUE_ERROR` and `GAME_ERROR` without crashing
- [ ] All messages include proper envelope fields and auth_token
- [ ] Timestamps are UTC with `Z` or `+00:00`
- [ ] Logs are in JSON Lines format
- [ ] History is persisted to `data/players/`
- [ ] At least one full test league run succeeds without errors

---

### 6.7 Frequently Asked Questions

#### 6.7.1 Can I use external libraries?

Yes. Standard libraries (`fastapi`, `pydantic`, `httpx`, `numpy`) are allowed. Avoid large ML frameworks unless for the optional LLM strategy.

#### 6.7.2 Must I use Python?

Python 3.10+ is strongly encouraged. Other languages (Java, JavaScript, Go) are possible if they can follow the `league.v2` protocol and run as HTTP servers.

#### 6.7.3 What if my agent crashes during the league?

- Log the error thoroughly
- Provide a recovery mechanism (restart from disk state)
- The referee will report a `TECHNICAL_LOSS` for unresponsive players

#### 6.7.4 Can I update my agent after submission?

Yes, but updates must maintain protocol compatibility. New features should not break existing interoperability.

#### 6.7.5 How do I know my ranking?

Query the League Manager with `LEAGUE_QUERY` (type: `"standings"`) or wait for `LEAGUE_STANDINGS_UPDATE` broadcasts.

---

### 6.8 Summary

The homework requires you to:

1. **Understand** the `league.v2` protocol and MCP architecture
2. **Design** a Player Agent with proper state and strategy modules
3. **Implement** the agent following all protocol rules and timing constraints
4. **Test** locally and document results
5. **Submit** a clean, well-documented codebase ready for integration with other students' agents

Upon completion, your agent can compete in the classroom league!

---

## Appendix: Key Protocol Violations to Avoid

### Common Mistakes

1. ❌ **Non-UTC Timestamps:** Always use `Z` or `+00:00`
2. ❌ **Missing auth_token:** Include after registration in every message
3. ❌ **Invalid parity_choice:** Only `"even"` or `"odd"` allowed
4. ❌ **Missing envelope fields:** Always include protocol, message_type, sender, timestamp, conversation_id
5. ❌ **Sender format:** Use `player:P01`, not just `P01`
6. ❌ **Responding after timeout:** Respect deadline fields
7. ❌ **Direct player-to-player communication:** Always route through Referee or Manager
8. ❌ **Crashing on invalid messages:** Log and ignore gracefully

---

**End of Part 3 & Homework Exercise Complete**
