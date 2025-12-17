# Homework Exercise: Even/Odd League - Part 2: Game Rules, Messages & Implementation Guide

**Dr. Yoram Segal © 2025**  
**Version 2.0**

---

## Section 3: The Even/Odd Game

### 3.1 Game Description

The Even/Odd game is simple and serves to demonstrate the league protocol.

#### 3.1.1 Game Rules

1. Two players participate
2. Each player chooses either "even" or "odd"
3. Choices are made simultaneously (without knowing the opponent's choice)
4. The Referee draws a random number between 1 and 10
5. If the number is even, the player who chose "even" wins
6. If the number is odd, the player who chose "odd" wins
7. If both chose correctly/incorrectly → Draw

#### 3.1.2 Example Game

Let's say Player A plays Player B:

| Outcome | Number | Player A Choice | Player B Choice |
|---------|--------|-----------------|-----------------|
| A wins | 8 (even) | even | odd |
| B wins | 7 (odd) | even | odd |
| Draw | 4 (even) | odd | odd |

---

### 3.2 Single Game Flow

#### 3.2.1 Stage 1: Game Invitation

The Referee sends an invitation to both players, including:
- Match ID (`match_id`)
- Round ID (`round_id`)
- Game type (`game_type`)

#### 3.2.2 Stage 2: Attendance Confirmation

Each player confirms arrival with `GAME_JOIN_ACK`.

#### 3.2.3 Stage 3: Collect Choices

The Referee asks each player to choose "even" or "odd". Players must respond within 30 seconds.

#### 3.2.4 Stage 4: Draw Number

After receiving both choices, the Referee draws a random number (1–10).

#### 3.2.5 Stage 5: Determine Winner

The Referee applies the rules to determine the winner.

#### 3.2.6 Stage 6: Report Result

The Referee sends:
1. `GAME_OVER` to both players
2. `MATCH_RESULT_REPORT` to the League Manager

---

### 3.3 Game States

The game transitions through defined states:

```
WAITING_FOR_PLAYERS
        ↓ (Both players ACK)
COLLECTING_CHOICES
        ↓ (Both choices received)
DRAWING_NUMBER
        ↓ (Result computed)
FINISHED
```

#### 3.3.1 WAITING_FOR_PLAYERS State

Initial state. Referee waits for both players to send `GAME_JOIN_ACK`.

Transition: Both players have confirmed.

#### 3.3.2 COLLECTING_CHOICES State

Referee collects parity choices from both players.

Transition: Both players have responded.

#### 3.3.3 DRAWING_NUMBER State

Referee draws the number and computes winner.

Transition: Automatic after calculation.

#### 3.3.4 FINISHED State

Game is complete, result reported.

---

### 3.4 Scoring

#### 3.4.1 Points per Game

| Outcome | Points for Winner | Points for Loser |
|---------|------------------|-----------------|
| Win | 3 | 0 |
| Draw | 1 | 1 |
| Loss | 0 | 0 |

#### 3.4.2 League Ranking

Ranking is determined by:

1. **Total Points** (descending)
2. **Number of Wins** (descending)
3. **Draw Count** (descending)

---

### 3.5 Round-Robin League

With 4 players, each player plays every other player once.

#### 3.5.1 Number of Games

For n players: `n × (n-1) / 2`

For 4 players: `4 × 3 / 2 = 6` games

#### 3.5.2 Example Schedule

| Game | Player A | Player B |
|------|----------|----------|
| R1M1 | P01 | P02 |
| R1M2 | P03 | P04 |
| R2M1 | P01 | P03 |
| R2M2 | P02 | P04 |
| R3M1 | P01 | P04 |
| R3M2 | P02 | P03 |

---

### 3.6 Strategies for Players

#### 3.6.1 Random Strategy

The simplest approach: randomly choose "even" or "odd". Win probability is 50% over many games.

```python
import random

def choose_parity_random():
    return random.choice(["even", "odd"])
```

#### 3.6.2 History-Based Strategy

The player remembers previous results and tries to detect patterns. Note: since draws are random, this won't improve long-term results but is an interesting exercise.

#### 3.6.3 LLM-Guided Strategy

Use a language model to decide. Example prompt:

```
You are playing Even/Odd game.
Choose "even" or "odd".
Previous results: even won 3 times, odd won 2 times.
Your choice (one word only):
```

Note: LLM won't provide statistical advantage but is educational.

---

### 3.7 Game Rules Module

The game rules are encapsulated in a separate module.

#### 3.7.1 Module Interface

The module provides:

- `init_game_state()` – Initialize game state
- `validate_choice(choice)` – Check if choice is valid
- `draw_number()` – Draw random number (1–10)
- `determine_winner(choices, number)` – Compute winner

#### 3.7.2 Advantage of Separation

Separating rules from protocol allows:

- Easy substitution of different games (Tic-Tac-Toe, 21 Questions, etc.)
- Protocol remains unchanged
- New games can be added without modifying core infrastructure

---

### 3.8 Extending to Other Games

The protocol is designed to be generic, not specific to Even/Odd.

#### 3.8.1 Generic Move Abstraction (GAME_MOVE)

The specific messages `CHOOSE_PARITY_CALL` and `CHOOSE_PARITY_RESPONSE` are instances of a generic abstraction:

| Generic Message | Even/Odd Specific |
|-----------------|------------------|
| GAME_MOVE_CALL | CHOOSE_PARITY_CALL |
| GAME_MOVE_RESPONSE | CHOOSE_PARITY_RESPONSE |

#### 3.8.2 Generic Move Message Structure

**Generic move request:**

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_MOVE_CALL",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:30:15Z",
  "match_id": "R1M1",
  "player_id": "P01",
  "game_type": "even_odd",
  "move_request": {
    "move_type": "choose_parity",
    "valid_options": ["even", "odd"],
    "deadline": "2025-01-15T10:30:45Z"
  }
}
```

#### 3.8.3 Game Registry (games_registry.json)

Future: A config file registering supported game types and their rules.

#### 3.8.4 Advantages of Abstraction

- Support multiple game types in one protocol
- New games can be added without protocol changes
- Clear separation of concerns

---

## Section 4: JSON Message Structures

This section defines the exact JSON structures for all message types.

### 4.1 Referee Registration Messages

#### 4.1.1 Referee Register Request (REFEREE_REGISTER_REQUEST)

```json
{
  "protocol": "league.v2",
  "message_type": "REFEREE_REGISTER_REQUEST",
  "sender": "referee:UNREGISTERED",
  "timestamp": "2025-01-15T08:00:00Z",
  "conversation_id": "conv-ref-reg-001",
  "referee_meta": {
    "display_name": "RefereeAlpha",
    "version": "1.0.0",
    "protocol_version": "2.1.0",
    "supported_games": ["even_odd"],
    "contact_endpoint": "http://localhost:8001/mcp"
  }
}
```

#### 4.1.2 Referee Register Response (REFEREE_REGISTER_RESPONSE)

```json
{
  "protocol": "league.v2",
  "message_type": "REFEREE_REGISTER_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-01-15T08:00:05Z",
  "conversation_id": "conv-ref-reg-001",
  "status": "ACCEPTED",
  "referee_id": "REF01",
  "auth_token": "tok_ref01_xyz789...",
  "league_id": "league_2025_even_odd",
  "reason": null
}
```

---

### 4.2 Player Registration Messages

#### 4.2.1 Player Register Request (LEAGUE_REGISTER_REQUEST)

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_REGISTER_REQUEST",
  "sender": "player:UNREGISTERED",
  "timestamp": "2025-01-15T09:00:00Z",
  "conversation_id": "conv-p01-reg-001",
  "player_meta": {
    "display_name": "AgentAlpha",
    "version": "1.0.0",
    "protocol_version": "2.1.0",
    "game_types": ["even_odd"],
    "contact_endpoint": "http://localhost:8101/mcp"
  }
}
```

#### 4.2.2 Player Register Response (LEAGUE_REGISTER_RESPONSE)

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_REGISTER_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-01-15T09:00:05Z",
  "conversation_id": "conv-p01-reg-001",
  "status": "ACCEPTED",
  "player_id": "P01",
  "auth_token": "tok_p01_abc123def456ghi789...",
  "league_id": "league_2025_even_odd",
  "reason": null
}
```

---

### 4.3 Round Messages

#### 4.3.1 Round Announcement (ROUND_ANNOUNCEMENT)

```json
{
  "protocol": "league.v2",
  "message_type": "ROUND_ANNOUNCEMENT",
  "sender": "league_manager",
  "timestamp": "2025-01-15T10:00:00Z",
  "conversation_id": "conv-round-1-001",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "matches": [
    {
      "match_id": "R1M1",
      "game_type": "even_odd",
      "player_A_id": "P01",
      "player_B_id": "P02",
      "referee_endpoint": "http://localhost:8001/mcp"
    },
    {
      "match_id": "R1M2",
      "game_type": "even_odd",
      "player_A_id": "P03",
      "player_B_id": "P04",
      "referee_endpoint": "http://localhost:8001/mcp"
    }
  ]
}
```

---

### 4.4 Game Messages

#### 4.4.1 Game Invitation (GAME_INVITATION)

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_INVITATION",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:30:00Z",
  "conversation_id": "conv-r1m1-001",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1",
  "game_invitation": {
    "game_type": "even_odd",
    "match_id": "R1M1",
    "role_in_match": "PLAYER_A",
    "opponent_id": "P02"
  }
}
```

#### 4.4.2 Game Join Acknowledgement (GAME_JOIN_ACK)

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_JOIN_ACK",
  "sender": "player:P01",
  "timestamp": "2025-01-15T10:30:02Z",
  "conversation_id": "conv-r1m1-001",
  "auth_token": "tok_p01_abc123...",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1",
  "accept": true
}
```

---

### 4.5 Parity Choice Messages

#### 4.5.1 Parity Choice Request (CHOOSE_PARITY_CALL)

```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_CALL",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:30:10Z",
  "conversation_id": "conv-r1m1-001",
  "auth_token": "tok_ref01_xyz789...",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1",
  "player_id": "P01",
  "parity_context": {
    "valid_options": ["even", "odd"],
    "your_standings": {
      "wins": 0,
      "losses": 0,
      "draws": 0
    },
    "opponent_id": "P02"
  },
  "deadline": "2025-01-15T10:30:40Z"
}
```

#### 4.5.2 Parity Choice Response (CHOOSE_PARITY_RESPONSE)

```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_RESPONSE",
  "sender": "player:P01",
  "timestamp": "2025-01-15T10:30:25Z",
  "conversation_id": "conv-r1m1-001",
  "auth_token": "tok_p01_abc123...",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1",
  "player_id": "P01",
  "parity_choice": "even"
}
```

---

### 4.6 Result Messages

#### 4.6.1 Game Over (GAME_OVER)

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_OVER",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:31:00Z",
  "conversation_id": "conv-r1m1-001",
  "auth_token": "tok_ref01_xyz789...",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1",
  "game_result": {
    "status": "WIN",
    "winner_player_id": "P01",
    "drawn_number": 8,
    "choices": {
      "P01": "even",
      "P02": "odd"
    }
  }
}
```

Status can be: `"WIN"`, `"DRAW"`, `"TECHNICAL_LOSS"`

#### 4.6.2 Match Result Report (MATCH_RESULT_REPORT)

```json
{
  "protocol": "league.v2",
  "message_type": "MATCH_RESULT_REPORT",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:31:05Z",
  "conversation_id": "conv-r1m1-001",
  "auth_token": "tok_ref01_xyz789...",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "match_id": "R1M1",
  "result": {
    "player_A": "P01",
    "player_B": "P02",
    "winner": "P01",
    "points_A": 3,
    "points_B": 0,
    "game_data": {
      "drawn_number": 8,
      "choice_A": "even",
      "choice_B": "odd"
    }
  }
}
```

---

### 4.7 Standings Messages

#### 4.7.1 League Standings Update (LEAGUE_STANDINGS_UPDATE)

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_STANDINGS_UPDATE",
  "sender": "league_manager",
  "timestamp": "2025-01-15T11:00:00Z",
  "conversation_id": "conv-standings-001",
  "auth_token": "tok_manager_abc...",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "standings": [
    {
      "rank": 1,
      "player_id": "P01",
      "points": 6,
      "wins": 2,
      "draws": 0,
      "losses": 0
    },
    {
      "rank": 2,
      "player_id": "P02",
      "points": 3,
      "wins": 1,
      "draws": 0,
      "losses": 1
    }
  ]
}
```

---

### 4.8 Completion Messages

#### 4.8.1 Round Completed (ROUND_COMPLETED)

```json
{
  "protocol": "league.v2",
  "message_type": "ROUND_COMPLETED",
  "sender": "league_manager",
  "timestamp": "2025-01-15T12:00:00Z",
  "conversation_id": "conv-round-1-completed",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "summary": {
    "total_matches": 3,
    "completed_matches": 3,
    "failed_matches": 0
  }
}
```

#### 4.8.2 League Completed (LEAGUE_COMPLETED)

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_COMPLETED",
  "sender": "league_manager",
  "timestamp": "2025-01-15T15:00:00Z",
  "conversation_id": "conv-league-completed",
  "league_id": "league_2025_even_odd",
  "final_standings": [
    {
      "rank": 1,
      "player_id": "P01",
      "points": 12,
      "wins": 4,
      "draws": 0,
      "losses": 2
    }
  ],
  "summary": {
    "total_rounds": 3,
    "total_matches": 6,
    "total_completed": 6
  }
}
```

---

### 4.9 Query Messages

#### 4.9.1 League Query (LEAGUE_QUERY)

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_QUERY",
  "sender": "player:P01",
  "timestamp": "2025-01-15T13:00:00Z",
  "conversation_id": "conv-query-001",
  "auth_token": "tok_p01_abc123...",
  "league_id": "league_2025_even_odd",
  "query_type": "standings"
}
```

#### 4.9.2 League Query Response (LEAGUE_QUERY_RESPONSE)

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_QUERY_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-01-15T13:00:02Z",
  "conversation_id": "conv-query-001",
  "league_id": "league_2025_even_odd",
  "query_type": "standings",
  "result": {
    "standings": [
      {
        "rank": 1,
        "player_id": "P01",
        "points": 6,
        "wins": 2
      }
    ]
  }
}
```

---

### 4.10 Error Messages

#### 4.10.1 LEAGUE_ERROR

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

#### 4.10.2 GAME_ERROR

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

---

### 4.11 Message Summary Table

| Message Type | Direction | Sender | Receiver |
|-------------|-----------|--------|----------|
| REFEREE_REGISTER_REQUEST | → | Referee | League Manager |
| REFEREE_REGISTER_RESPONSE | ← | League Manager | Referee |
| LEAGUE_REGISTER_REQUEST | → | Player | League Manager |
| LEAGUE_REGISTER_RESPONSE | ← | League Manager | Player |
| ROUND_ANNOUNCEMENT | → | League Manager | All |
| GAME_INVITATION | → | Referee | Players |
| GAME_JOIN_ACK | → | Player | Referee |
| CHOOSE_PARITY_CALL | → | Referee | Player |
| CHOOSE_PARITY_RESPONSE | → | Player | Referee |
| GAME_OVER | → | Referee | Player |
| MATCH_RESULT_REPORT | → | Referee | League Manager |
| LEAGUE_STANDINGS_UPDATE | → | League Manager | Player |
| ROUND_COMPLETED | → | League Manager | All |
| LEAGUE_COMPLETED | → | League Manager | All |
| LEAGUE_QUERY | → | Player | League Manager |
| LEAGUE_QUERY_RESPONSE | ← | League Manager | Player |
| LEAGUE_ERROR | → | League Manager | Recipient |
| GAME_ERROR | → | Referee | Player |

---

### 4.12 Important Rules

#### 4.12.1 Required Fields

Every message must include:
- `protocol: "league.v2"`
- `message_type`
- `sender` (in format `type:id`)
- `timestamp` (UTC ISO-8601)
- `conversation_id`

#### 4.12.2 Allowed Values

- `parity_choice`: only `"even"` or `"odd"`
- `status` (registration): `"ACCEPTED"` or `"REJECTED"`
- `game_result.status`: `"WIN"`, `"DRAW"`, `"TECHNICAL_LOSS"`
- `role_in_match`: `"PLAYER_A"` or `"PLAYER_B"`

#### 4.12.3 Timestamp Format

- Required: UTC with `Z` or `+00:00`
- Examples: `2025-01-15T10:30:00Z` ✓
- Invalid: `2025-01-15T10:30:00+02:00` ✗
- Invalid: `2025-01-15T10:30:00` ✗

---

**End of Part 2**
