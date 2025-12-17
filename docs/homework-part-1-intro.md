# Homework Exercise: Even/Odd League - Part 1: Introduction & Protocol Fundamentals

**Dr. Yoram Segal © 2025**  
**Version 2.0**

---

## Section 1: Introduction - AI Agents and MCP Protocol

### 1.1 What is an AI Agent?

An AI Agent is autonomous software.

**Key Properties:**
- **Autonomy** – The agent acts independently
- **Perception** – The agent collects information from its environment
- **Action** – The agent influences its environment
- **Goal-Orientation** – The agent has a defined purpose

The agent differs from regular programs: a regular program follows predetermined instructions. An AI agent decides what to do based on the current state.

**Reference:** Dr. Segal's book "AI Agents with MCP" covers how agents communicate.

---

### 1.2 MCP Protocol – Model Context Protocol

**MCP** is a communication protocol developed by Anthropic that enables AI agents to communicate with each other.

#### 1.2.1 Protocol Principles

1. **Structured Messages** – Every message is a JSON object
2. **JSON-RPC 2.0 Standard** – The protocol uses this standard
3. **Tools** – Agents expose functions as "tools"
4. **Flexible Transport** – Can use HTTP or stdio

#### 1.2.2 Host/Server Architecture

The MCP system has two types of components:

**MCP Server** – A component that provides services and exposes "tools" (functions with defined parameters).

**Host (Orchestrator)** – A component that coordinates between servers, sending requests and processing responses.

```
Host (Orchestrator)
    ↓
    ├─ MCP Server 1 (JSON-RPC)
    ├─ MCP Server 2 (JSON-RPC)
    └─ MCP Server 3 (JSON-RPC)
```

---

### 1.3 HTTP Transport on Localhost

In this exercise, we use HTTP transport. Each agent runs on a different port on localhost.

#### 1.3.1 Port Definitions

- **League Manager** – Port 8000
- **Referee** – Port 8001
- **Players** – Ports 8101–8104

#### 1.3.2 Agent Endpoint Examples

- League Manager: `http://localhost:8000/mcp`
- Player 1: `http://localhost:8101/mcp`
- Referee 1: `http://localhost:8001/mcp`

All agents implement a simple HTTP server. The `/mcp` endpoint accepts POST requests containing JSON-RPC 2.0.

---

### 1.4 JSON-RPC 2.0 Message Structure

Every message in the protocol is a JSON object with a fixed structure:

```json
{
  "jsonrpc": "2.0",
  "method": "tool_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "id": 1
}
```

**Message Fields:**

- `jsonrpc` – Protocol version, always `"2.0"`
- `method` – Name of the tool to invoke (e.g., `register_player`, `game_invitation`)
- `params` – Parameters for the tool
- `id` – Unique identifier for the request (for matching responses)

---

### 1.5 Exercise Goals

In this exercise, we build a league system for AI agents. The system includes three agent types:

1. **League Manager** – Manages the tournament, player registration, and standings
2. **Referee** – Manages individual games and determines winners
3. **Player Agents** – Participate in games

#### 1.5.1 Learning Objectives

Upon completion, you will:

- Understand the MCP protocol
- Build a simple MCP server
- Enable communication between different agents
- Run a complete league in your local environment
- Ensure protocol compatibility with other students' agents

**Important:** All students use the same protocol. This allows your agents to play against other students' agents in a classroom league.

---

## Section 2: General League Protocol

### 2.1 Protocol Principles

The protocol defines uniform rules enabling agents from different implementations to communicate.

#### 2.1.1 Three-Layer Separation

The system is organized into three distinct layers:

1. **League Layer** – Tournament management, player registration, ranking table
2. **Referee Layer** – Individual game management, move validation, winner declaration
3. **Game Rules Layer** – Game-specific logic (Even/Odd, Tic-Tac-Toe, etc.)

This separation allows swapping out the game rules layer without changing the protocol.

---

### 2.2 Agent Types

#### 2.2.1 League Manager

The League Manager is a singleton agent responsible for:

- Registering players into the league
- Creating a schedule (Round-Robin tournament)
- Receiving results from referees
- Computing and publishing the ranking table

The League Manager operates as an MCP server on port 8000.

#### 2.2.2 Referee

The Referee manages a single game. **Before refereing games, the Referee must register with the League Manager.**

The Referee is responsible for:

- Registering with the League Manager (before the league starts)
- Inviting two players to a game
- Managing the game flow (turn-taking, move validation)
- Declaring the winner
- Reporting the result to the League Manager

The Referee operates as an MCP server on port 8001 (multiple referees on 8001–8010).

#### 2.2.3 Player Agent

The Player Agent represents a player in the league and is responsible for:

- Registering with the League Manager
- Accepting game invitations
- Making moves in the game
- Updating internal state based on results

Each Player operates on a separate port (8101–8104).

---

### 2.3 Identifiers in the Protocol

Each component in the system has a unique identifier:

| Identifier | Type | Examples |
|-----------|------|----------|
| `league_id` | String | `"league_2025_even_odd"` |
| `round_id` | Integer | `1, 2, 3, ...` |
| `match_id` | String | `"R1M1"` (Round 1, Match 1) |
| `game_type` | String | `"even_odd"`, `"tic_tac_toe"` |
| `player_id` | String | `"P01"`, `"P02"`, ... `"P20"` |
| `referee_id` | String | `"REF01"`, `"REF02"`, ... |
| `conversation_id` | String | `"conv-r1m1-001"` |

---

### 2.4 Message Envelope (General Structure)

Every message in the protocol must include an **envelope** with fixed fields. The envelope ensures consistency and enables message tracking.

#### Message Envelope Structure

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_INVITATION",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:30:00Z",
  "conversation_id": "conv-r1m1-001",
  "auth_token": "tok_abc123def456...",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1"
}
```

#### 2.4.1 Required Envelope Fields

| Field | Type | Description |
|-------|------|-------------|
| `protocol` | String | Protocol version, constant: `"league.v2"` |
| `message_type` | String | Message type (e.g., `GAME_INVITATION`) |
| `sender` | String | Identifier of sender in format `type:id` |
| `timestamp` | String | ISO-8601 timestamp in UTC |
| `conversation_id` | String | Unique conversation identifier |

#### 2.4.2 UTC/GMT Timezone Requirement

**Important:** All timestamps in the protocol must be in UTC/GMT. This ensures consistency across agents in different geographic locations.

| Format | Valid? | Explanation |
|--------|--------|-------------|
| `2025-01-15T10:30:00Z` | ✓ | Z suffix indicates UTC |
| `2025-01-15T10:30:00+00:00` | ✓ | +00:00 equals UTC |
| `2025-01-15T10:30:00+02:00` | ✗ | Local timezone – forbidden |
| `2025-01-15T10:30:00` | ✗ | No timezone – forbidden |

**Error Consequence:** An agent sending a non-UTC timestamp will receive error `E021 (INVALID_TIMESTAMP)`.

#### 2.4.3 Optional Fields (Context-Dependent)

| Field | Type | Description |
|-------|------|-------------|
| `auth_token` | String | Authentication token (required after registration) |
| `league_id` | String | League identifier |
| `round_id` | Integer | Round number |
| `match_id` | String | Match identifier |

#### 2.4.4 Sender Field Format

The `sender` field identifies the message sender:

- `league_manager` – The League Manager
- `referee:REF01` – Referee with ID REF01
- `player:P01` – Player with ID P01

#### 2.4.5 Authentication Token (auth_token)

After successful registration, each agent receives an `auth_token`. This token must be included in every subsequent message. The token prevents impersonation.

**Example registration response:**

```json
{
  "message_type": "LEAGUE_REGISTER_RESPONSE",
  "status": "ACCEPTED",
  "player_id": "P01",
  "auth_token": "tok_p01_abc123def456ghi789..."
}
```

---

### 2.5 Overall League Flow

#### 2.5.1 Stage 1: Register Referees

Referees register with the League Manager.

```
Referee → REFEREE_REGISTER_REQUEST → League Manager
League Manager → REFEREE_REGISTER_RESPONSE → Referee
```

#### 2.5.2 Stage 2: Register Players

Players register with the League Manager.

```
Player → LEAGUE_REGISTER_REQUEST → League Manager
League Manager → LEAGUE_REGISTER_RESPONSE → Player
```

#### 2.5.3 Stage 3: Create Schedule

After all players register, the League Manager creates a Round-Robin schedule (each player plays every other player).

#### 2.5.4 Stage 4: Announce Round

Before each round, the League Manager announces all matches for that round via `ROUND_ANNOUNCEMENT`.

#### 2.5.5 Stage 5: Manage Matches

Referees conduct individual matches following the game rules.

#### 2.5.6 Stage 6: Update Rankings

After each round, the League Manager updates and publishes the standings.

---

### 2.6 Overall Flow Diagram

```
Start
  ↓
Register Referees
  ↓
Register Players
  ↓
Create Schedule
  ↓
More Matches?
  ├─ Yes → Run Match → Update Standings → (back to "More Matches?")
  └─ No → End
```

---

### 2.7 Response Timeouts

Each message type has a maximum response time. If an agent doesn't respond in time, the action is considered failed.

| Message Type | Timeout | Notes |
|-------------|---------|-------|
| REFEREE_REGISTER | 10 sec | Referee registration |
| LEAGUE_REGISTER | 10 sec | Player registration |
| GAME_JOIN_ACK | 5 sec | Game invitation confirmation |
| CHOOSE_PARITY | 30 sec | Even/Odd choice |
| GAME_OVER | 5 sec | Game result receipt |
| MATCH_RESULT_REPORT | 10 sec | Result sent to League Manager |
| LEAGUE_QUERY | 10 sec | Information query |
| All Others | 10 sec | Default timeout |

---

### 2.8 Agent Lifecycle

Each agent (player, referee) goes through defined states during the league.

#### 2.8.1 Agent States

- **INIT** – Agent started, not yet registered
- **REGISTERED** – Agent successfully registered and received `auth_token`
- **ACTIVE** – Agent is participating in games
- **SUSPENDED** – Agent is temporarily inactive (not responding)
- **SHUTDOWN** – Agent has finished

#### 2.8.2 State Transition Diagram

```
INIT
  ↓ (register)
REGISTERED
  ↓ (league_start)
ACTIVE
  ↕ (timeout/recover)
SUSPENDED
  ↓ (league_end / error / max_fail)
SHUTDOWN
```

---

### 2.9 Error Handling

The protocol defines two types of error messages:

#### 2.9.1 League Error (LEAGUE_ERROR)

The League Manager sends this when a league-level error occurs.

**Example:**

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_ERROR",
  "sender": "league_manager",
  "timestamp": "2025-01-15T10:35:00Z",
  "error_code": "E005",
  "error_name": "PLAYER_NOT_REGISTERED",
  "error_description": "Player ID not found in registry",
  "context": {
    "player_id": "P99"
  },
  "retryable": false
}
```

#### 2.9.2 Game Error (GAME_ERROR)

The Referee sends this when a game-level error occurs.

**Example:**

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_ERROR",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:31:00Z",
  "match_id": "R1M1",
  "player_id": "P01",
  "error_code": "E001",
  "error_name": "TIMEOUT_ERROR",
  "error_description": "Response not received within 30 seconds",
  "game_state": "COLLECTING_CHOICES",
  "retryable": true,
  "retry_count": 1,
  "max_retries": 3
}
```

#### 2.9.3 Common Error Codes

| Code | Name | Description |
|------|------|-------------|
| E001 | TIMEOUT_ERROR | Response not received in time |
| E003 | MISSING_REQUIRED_FIELD | Required field missing |
| E004 | INVALID_PARITY_CHOICE | Invalid choice (not "even" or "odd") |
| E005 | PLAYER_NOT_REGISTERED | Player ID not found |
| E009 | CONNECTION_ERROR | Connection failure |
| E011 | AUTH_TOKEN_MISSING | Auth token not included |
| E012 | AUTH_TOKEN_INVALID | Auth token is invalid |
| E018 | PROTOCOL_VERSION_MISMATCH | Protocol version incompatible |

#### 2.9.4 Retry Policy

Retryable errors can be attempted again:

- **Maximum Retries:** 3
- **Backoff Between Retries:** 2 seconds
- **Retryable Errors:** `E001` (timeout), `E009` (connection)
- **After Max Retries:** Technical loss

---

### 2.10 Version Compatibility

#### 2.10.1 Version Declaration

When registering, each agent declares the protocol version it supports.

**Example in registration request:**

```json
{
  "message_type": "LEAGUE_REGISTER_REQUEST",
  "player_meta": {
    "display_name": "Agent Alpha",
    "version": "1.0.0",
    "protocol_version": "2.1.0",
    "game_types": ["even_odd"]
  }
}
```

#### 2.10.2 Compatibility Policy

- **Current Version:** 2.1.0
- **Minimum Supported:** 2.0.0
- Agents with older protocol versions receive error `E018 (PROTOCOL_VERSION_MISMATCH)`

---

### 2.11 Important Principles

#### 2.11.1 Single Source of Truth

The Referee is the single source of truth for game state. Players do not maintain their own game state; they rely on information from the Referee.

#### 2.11.2 Communication Through Orchestrator

Players do not communicate directly with each other. All communication flows through the Referee or League Manager. This ensures protocol integrity.

#### 2.11.3 Failure Handling

If a player doesn't respond:

1. Referee sends `GAME_ERROR` with `retryable=true`
2. Player gets up to 3 attempts to respond
3. After max retries → Technical loss (`TECHNICAL_LOSS`)

---

**End of Part 1**
