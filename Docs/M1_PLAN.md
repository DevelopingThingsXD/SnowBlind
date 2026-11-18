# M1: Core Duel (implementation plan)

Branch: `m1-core-duel`. Design source: [DESIGN.md](DESIGN.md) §4 and §15.
Exit criterion: **one duel is fun to replay 10× in a row and every loss can be read.**

M1 changes the round flow only. Charms (the existing power-ups) stay as they are. Run state, items, and captor data come in M2.

## Current jam flow (for reference)
`Player_BP.ReleaseCard` (card dropped on the `PlayerPlayArea` tag) → `CardWar_GM.PlayerPlayedCard` → `OpponentPlayCard`
(opponent commits) → custom event `CardPlay_Sequence`: delay → `PresentCards` (flip) → compare `modifiedValue`/`cardValue` →
loser lives −1 → `BlowoutCandle` → destroy played cards → `RefreshCardLocations` → unlock input → 0 lives → cannon `LookAt` → `ShootLoser`.

## New flow

```
StartRound ─► Draw (both hands back up to 5 number cards; deck refills when empty)
          ─► Play (player drags a card in; opponent commits)
          ─► Wager (first to act alternates; hold/raise → call/fold/re-raise)
                ├─ fold ─► FoldReveal (show both cards briefly) ─► folder −1 ─► Cleanup
                └─ settled ─► Reveal (cannon notches = stake; held beat if stake ≥ 2; flip; big number)
                               ─► Resolve (tie → carry +1; else loser −stake candles; loss summary line)
          ─► Cleanup (destroy played cards, re-fan hands) ─► game over? ─► else StartRound
```

## Rules in M1
- **Stake** = `1 + TieCarry`. Raise +1; one re-raise +1 more (max one re-raise per round).
- You can only raise if **your lives > current stake** (you can't bet candles you don't have).
- **First to act** alternates every round (round 1: player).
- **Fold** costs 1 life (not the stake). A fold never pays out a raised pot. Folded cards are shown for ~1.5 s.
- **Tie:** both cards are buried and `TieCarry += 1` (it accumulates until a round is decided, then resets to 0).
- **Loss summary** (General_WBP line), e.g. *"His 9 beat your 7. 3 higher cards were still out there."*

## Assets & changes

| Asset | Change |
|---|---|
| `E_RoundPhase` (new enum) | Draw, Play, Wager, Reveal, Resolve, Cleanup, GameOver |
| `E_WagerAction` (new enum) | Hold, Raise, Call, Fold, ReRaise |
| `CardWar_GM` | Vars: `Phase`, `RoundIndex`, `Stake`, `TieCarry`, `PlayerActsFirst`, `ReRaiseUsed`, `WagerWidget`. Functions: `StartRound`, `DrawToFive(side)`, `BeginWager`, `SubmitWager(isPlayer, action)`, `RevealAndResolve`, `ResolveFold(playerFolded)`, `LoseLives(isPlayer, n)`, `BuildLossSummary`, `CountHigherRemaining(value)`. `PlayerPlayedCard` routes to `BeginWager` instead of `CardPlay_Sequence` |
| `Opponent_BP` | Vars: `Aggression` (0.4), `BluffRate` (0.1). Function `DecideWager(facingRaise, stake) → E_WagerAction` based on final card value vs remaining-deck average |
| `WBP_Wager` (new widget) | Prompt text + buttons Hold/Raise or Call/Fold/Re-raise; calls `CardWar_GM.SubmitWager`; shows/hides the cursor |
| `Cannon_BP` | `SetStakeAim(stake)`: a small creaking turn toward the table per candle at stake (+ `GunAdjust` SFX) |
| `General_WBP` | `SummaryText` TextBlock + `ShowSummary(text)` (fade in, hold, fade out) |
| `Player_BP` | Input gate: cards can only be played in the `Play` phase |

## Out of scope for M1 (noted for M2+)
GameInstance run state and the descent deck across levels, charms rework, items, captor data assets/tells, darkness rules, diegetic wager input (pushing candles forward).
