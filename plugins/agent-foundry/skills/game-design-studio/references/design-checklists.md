# Game Design Checklists

## Core Loop

- What is the player's repeated verb?
- What creates pressure?
- What creates reward?
- What changes after the loop?
- What makes the player want one more loop?

## System Design

- What state does the system own?
- What inputs does it consume?
- What outputs does it produce?
- Which systems depend on it?
- What values are tunable?
- What edge cases can break the fantasy?

## Economy

- Source: where resources enter.
- Sink: where resources leave.
- Conversion: how one resource becomes another.
- Constraint: what blocks optimal hoarding.
- Risk: how players can exploit the economy.

## Encounter

- Primary objective
- Secondary objective
- Pressure source
- Twist
- Reward
- Exit condition

## Acceptance Criteria

Good criteria are observable, testable, and implementation-relevant:

- Player can do X under condition Y.
- System produces value Z from input A/B.
- Edge case E resolves with behavior R.
- UI communicates state S within N seconds/actions.
- Config value lives in data, not hardcoded code.
