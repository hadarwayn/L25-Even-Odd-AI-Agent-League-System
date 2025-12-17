# Even/Odd League API Documentation

## Protocol Overview

The Even/Odd League uses the `league.v2` protocol over JSON-RPC 2.0 with HTTP transport.

### Base URL Structure
```
http://{host}:{port}/mcp
```

### Standard Ports
| Agent | Port |
|-------|------|
| League Manager | 8000 |
| Referee REF01 | 8001 |
| Referee REF02 | 8002 |
| Player P01 | 8101 |
| Player P02 | 8102 |
| Player P03 | 8103 |
| Player P04 | 8104 |

---

## Message Envelope

All messages must include these envelope fields:

```json
{
  "protocol": "league.v2",
  "message_type": "MESSAGE_TYPE",
  "sender": "player:P01",
  "timestamp": "2025-01-15T10:30:00Z",
  "conversation_id": "uuid-string",
  "auth_token": "token-after-registration"
}
```

### Timestamp Format
- Must be UTC with Z suffix: `2025-01-15T10:30:00Z`
- Or with +00:00 offset: `2025-01-15T10:30:00+00:00`
- Non-UTC timestamps are rejected

### Sender Format
- Players: `player:P01`, `player:P02`, etc.
- Referees: `referee:REF01`, `referee:REF02`, etc.
- League Manager: `league_manager`

---

## Registration Messages

### LEAGUE_REGISTER_REQUEST
Player/Referee registration with League Manager.

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_REGISTER_REQUEST",
  "sender": "player:UNREGISTERED",
  "timestamp": "2025-01-15T10:00:00Z",
  "conversation_id": "uuid",
  "player_meta": {
    "display_name": "AlphaBot",
    "contact_endpoint": "http://127.0.0.1:8101/mcp",
    "game_types": ["even_odd"],
    "version": "1.0.0"
  }
}
```

### LEAGUE_REGISTER_RESPONSE
```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_REGISTER_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-01-15T10:00:01Z",
  "conversation_id": "uuid",
  "status": "REGISTERED",
  "player_id": "P01",
  "auth_token": "tok_abc123xyz"
}
```

Status values: `REGISTERED`, `REJECTED`

---

## Game Messages

### GAME_INVITATION
Referee invites player to a match.

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_INVITATION",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:30:00Z",
  "conversation_id": "match-uuid",
  "match_id": "R1M1",
  "round_id": "ROUND_1",
  "game_type": "even_odd",
  "opponent_id": "P02",
  "role": "PLAYER_A"
}
```

### GAME_JOIN_ACK
Player accepts game invitation.

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_JOIN_ACK",
  "sender": "player:P01",
  "timestamp": "2025-01-15T10:30:05Z",
  "conversation_id": "match-uuid",
  "auth_token": "tok_abc123",
  "match_id": "R1M1",
  "accept": true
}
```

### CHOOSE_PARITY_CALL
Referee asks player for parity choice.

```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_CALL",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:30:10Z",
  "conversation_id": "match-uuid",
  "match_id": "R1M1",
  "deadline": "2025-01-15T10:30:40Z"
}
```

### CHOOSE_PARITY_RESPONSE
Player's parity choice.

```json
{
  "protocol": "league.v2",
  "message_type": "CHOOSE_PARITY_RESPONSE",
  "sender": "player:P01",
  "timestamp": "2025-01-15T10:30:15Z",
  "conversation_id": "match-uuid",
  "auth_token": "tok_abc123",
  "match_id": "R1M1",
  "parity_choice": "even"
}
```

Valid choices: `even`, `odd`

### GAME_OVER
Match result notification.

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_OVER",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:31:00Z",
  "conversation_id": "match-uuid",
  "match_id": "R1M1",
  "drawn_number": 7,
  "your_choice": "odd",
  "opponent_choice": "even",
  "result": "WIN",
  "points_earned": 3
}
```

Result values: `WIN`, `LOSS`, `DRAW`, `TECHNICAL_LOSS`

---

## Query Messages

### QUERY_STANDINGS_REQUEST
```json
{
  "protocol": "league.v2",
  "message_type": "QUERY_STANDINGS_REQUEST",
  "sender": "player:P01",
  "timestamp": "2025-01-15T11:00:00Z",
  "conversation_id": "uuid",
  "auth_token": "tok_abc123"
}
```

### QUERY_STANDINGS_RESPONSE
```json
{
  "protocol": "league.v2",
  "message_type": "QUERY_STANDINGS_RESPONSE",
  "sender": "league_manager",
  "timestamp": "2025-01-15T11:00:01Z",
  "conversation_id": "uuid",
  "standings": [
    {"rank": 1, "player_id": "P04", "points": 7, "wins": 2, "draws": 1, "losses": 0}
  ]
}
```

---

## Error Messages

### LEAGUE_ERROR
```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_ERROR",
  "sender": "league_manager",
  "timestamp": "2025-01-15T10:00:01Z",
  "conversation_id": "uuid",
  "error_code": "E005",
  "error_name": "PLAYER_NOT_REGISTERED",
  "error_description": "Player ID not found in registry",
  "retryable": false
}
```

### Error Codes

| Code | Name | Description | Retryable |
|------|------|-------------|-----------|
| E001 | TIMEOUT_ERROR | Response not received in time | Yes |
| E002 | INVALID_MESSAGE | Malformed message | No |
| E003 | PROTOCOL_MISMATCH | Wrong protocol version | No |
| E004 | INVALID_PARITY_CHOICE | Not 'even' or 'odd' | No |
| E005 | PLAYER_NOT_REGISTERED | Unknown player ID | No |
| E006 | MATCH_NOT_FOUND | Unknown match ID | No |
| E007 | OUT_OF_TURN | Action at wrong time | No |
| E008 | DEADLINE_PASSED | Response too late | No |
| E009 | CONNECTION_ERROR | Network failure | Yes |
| E010 | RATE_LIMITED | Too many requests | Yes |
| E011 | AUTH_TOKEN_MISSING | No auth token | No |
| E012 | AUTH_TOKEN_INVALID | Wrong auth token | No |

---

## Scoring System

| Result | Points |
|--------|--------|
| WIN | 3 |
| DRAW | 1 |
| LOSS | 0 |
| TECHNICAL_LOSS | 0 |

---

## Response Deadlines

| Action | Deadline |
|--------|----------|
| GAME_JOIN_ACK | 5 seconds |
| CHOOSE_PARITY_RESPONSE | 30 seconds |
| Registration | 10 seconds |

---

## Health Check Endpoint

```
GET http://{host}:{port}/health
```

Response:
```json
{
  "status": "healthy",
  "agent": "player:P01"
}
```
