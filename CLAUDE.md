# SnowBlind — project map

Blueprint-only Unreal Engine **5.8** project (no C++ / no `Source/`). Upgraded from 5.6 on 2026-11-18;
most assets are still saved as 5.6 and upgrade on load. Engine install: `B:\UE_5.8`.

**The game:** a first-person, seated, high-stakes card duel ("CardWar"). You sit at a table across from a
captor/opponent. Each round both sides play one numbered card, wager candles (lives), and the higher value
wins. Lose all 3 candles and a cannon turns and shoots you. Win and you move to the next location.
Three locations: Courtyard (1) → Elevator (2) → Cave (3) → back to Main Menu.

**Direction:** the jam build is being expanded into a roguelite "descent". Design + roadmap:
[Docs/DESIGN.md](Docs/DESIGN.md). Current milestone: **M1 core duel**, [Docs/M1_PLAN.md](Docs/M1_PLAN.md),
on branch `m1-core-duel`. The rules below describe what is **implemented now**.

## Rules (implemented — `CardWar_GM`, `Opponent_BP`, `Card_BP`)

- **Deck:** one shared 40-card deck: values 1–10, four of each (`CardWar_GM.initialDeck`). Draws remove from
  it. It refills with a fresh 40 when it's empty (`RefillDeck`).
- **Hands:** each side starts with **5 number cards + 2 power-up cards**. At the start of every round both sides
  **draw back up to 5 number cards** (`StartRound` → `DrawToFive`).
- **Power-ups** drawn from the `Power Up Deck` map: **×2**, **+5**, **+3**. Applying one sets `Card_BP.modifiedValue`.
  `FinalValue(card)` = `modifiedValue` if set, else `cardValue`.
- **Round flow** (custom events on `CardWar_GM`):
  `StartRound` (draw, toggle `PlayerFirst`, unlock input) → player drags a card into the play area →
  `PlayerPlayedCard` → `CardPlay_Sequence` (`PrepareOpponentHand` moves a random number card to index 0,
  then `Opponent_BP.PlayCard`) → `OpponentPlayCard` → **`BeginWager`** → **`RevealRound`** or **`FoldRound`** →
  `CleanupRound` → `StartRound` (unless someone is at 0 lives).
- **Wagers:** stake starts at `1 + TieCarry`. The **first to act alternates** every round (`PlayerFirst`).
  The first actor **holds** or **raises** (+1). The responder **calls**, **folds** (loses 1, cards shown briefly),
  or **re-raises once** (+1). You can only raise if your lives > current stake. `WagerState`: 0 none,
  1 = player opens, 2 = player facing an AI raise, 3 = player facing an AI re-raise.
- **Candles are the chips.** All 6 candles stay lit. When you lose, the candles at stake **slide to the winner's
  row** and become their lives (`LoseLives(loser, amount)` moves actors between `PlayerLifeCandles` and
  `OpponentLifeCandles`; `LayoutCandles` places them using the origin and step taken from each level's placed
  candles in `InitCandleLayout`; `LifeCandle_BP.MoveTo` glides there on Tick). Lives = candle count. 0 candles → cannon.
- **Your played card turns face-up toward you** during the wager (`PlayerPlayedCard`); his stays face-down.
- **Reveal:** a held beat if the stake is above 1 → flip → floating numbers → the higher `FinalValue` wins → the stake
  moves to the winner. The cannon clicks a notch per raise (`CannonNotch`).
- **Tie:** both cards are buried and `TieCarry += 1`, so the next round's stake is higher. (The jam's random ±1–3
  nudge was removed.)
- **Round summary** (HUD, top): e.g. "His ten beat your six / You lose three candles / There were still
  fourteen higher cards in the deck".
- **Lives:** 3 each, shown as 6 `LifeCandle_BP` actors (0–2 player, 3–5 opponent).
- **Game over:** `Cannon_BP.LookAt` at the loser → `ShootLoser` → `General_WBP.GameOver` → next level / menu.
- **Opponent AI:** card choice is a random number card. Wager choice: `Opponent_BP.DecideWager` compares its
  `FinalValue` against `CardWar_GM.OpponentUnseenAverage` (deck + player's hand). It raises at +2 strength
  or on a bluff (`BluffRate` 0.15), re-raises at +3, calls at −1 or better, otherwise folds. Power-up use is
  still the jam logic (`PlayCard` + `ChoosePowerUpDeck`, ×2 on cards ≥ 6), using `RemainingCardAverage`,
  which `StartRound` now sets from `OpponentUnseenAverage`.
- **Known balance issue:** a raise plus a re-raise can take all 3 candles in round 1. Per DESIGN §5, wagers should
  unlock from floor 2 (M2).
- `Power Up Spawn Chance` on the GM is unused. The old `PresentCards` event is unused (kept for reference).

## Controls (`Player_BP`)

Mouse look (clamped) • **Left click/drag** number cards into the play area • **Right click** a power-up onto a
card • **Hold Space** = freelook • **R** raise / re-raise, **C** hold / call, **F** fold (wager keys →
`CardWar_GM.PlayerWager(Action)`; 0 = hold/call, 1 = raise, 2 = fold). Input is locked (`bInputLocked`) from card
release until the next `StartRound`.

## HUD (`UI/General_WBP`)

`WagerPrompt_Txt` (bottom) and `Summary_Txt` (top) via `SetPrompt` / `SetSummary` (GM wrappers `ShowPrompt`,
`ShowSummary`). These two use **Roboto** (engine font, safe to ship) because **CS Aspen Drawn has NO digits or
punctuation** (they render as boxes). Keep the blackletter font for letters-only titles only (`NumberWord`
spells out numbers if you ever need it). `csaspendrawn-regular_Font` has no glyphs at all.

## Level flow

| Map | Game mode | Notes |
|---|---|---|
| `Levels/MainMenu_L` (startup + editor default) | `MainMenu_GM` + `MainMenu_Pawn_BP` | 3D menu cards (`MainMenuCard_BP`): Play → `Courtyard_L`, Quit |
| `Levels/Courtyard_L`: level 1 | project default `CardWar_GM` | snowy temple courtyard, braziers, wind/snow FX; opponent = hooded figure |
| `Levels/Elevator_L`: level 2 | `CardWar_GM` | moving elevator shaft, `ElevatorCameraShake_CS`; prisoner opponent |
| `Levels/Cave_L`: level 3 (final) | `CardWar_GM` | mine cave (minecart, crane, gemstones, water drips), chain splines; prisoner opponent; win → MainMenu |
| `TestLevel_v2_L`, `Basic_L`, `TestLevel` | — | test/scratch maps |

Next-level routing lives in `Blueprints/v2/UI/General_WBP` (`GameOver`: switch on current level name → `Open Level`).

## Where things live

- **`Content/Blueprints/v2/`**: ⭐ the live game.
  - `Blueprints/CardWar_GM`: GameModeBase. Deck, hands, lives, round/wager flow, win/lose, spawning cards.
  - `Blueprints/Player_BP`: Pawn: camera, hover line-trace, pickup/release/drag, power-ups, wager keys.
  - `Blueprints/Opponent_BP`: AI opponent (mesh, hand slots, card/power-up/wager choice).
  - `Blueprints/Card_BP`: a card: value, modifiedValue, power-up data, `CardState_Enum`
    (IdleInHand, Hovered, Dragging, Played, Resolved), fan positioning, chains, text.
  - `Cannon_BP` (uses Timelines; don't rewrite its graph with the DSL), `LifeCandle_BP`, `PlayArea_Player_BP`,
    `ChainSpline_BP`, `TextRenderCardValue_BP` (floating value at reveal; destroys itself).
  - `MainMenu/`: menu GM, pawn, menu cards. `UI/General_WBP` (HUD), `UI/MainMenu_UI`.
- **`Content/Blueprints/*.uasset` (v1)**: **legacy, unused by any game level** (old interaction system, tie wheel,
  `E_Difficulty`, `E_CardSide`). Only `TestLevel` uses them.
- **`Content/BP_*.uasset` + `NewBlueprint`** (root, ~2 KB each): **redirectors**. Fix up before deleting.
- `Content/Art/`, `Content/Audio/`, `Content/Fonts/`: see the art direction below.

## Art direction (observed)

Lo-fi retro 3D horror: low internal resolution via post-process resolution limiter, hand-painted textures,
moody fog, warm firelight (braziers, candles) against cold snow/moon/stars, emissive glowing card numbers,
chains on powered-up cards, hand-drawn blackletter font. Prisoner/captor framing: you gamble for your life.

## Rendering / project settings

Lumen off, Nanite off, VSM off, static lighting allowed, no AA, auto-exposure off, DX12 SM6.

## Working on this project with Claude

**Read-only, editor closed or open:** `python Tools/bp_index.py` → `Saved/BlueprintIndex/*.txt` (variables +
defaults, every graph's nodes and literal pin values, no wires). Never `Read`/`Edit` `.uasset`/`.umap` directly.

**Live editing (editor open):**
- `Tools/ue/uepy.py <file.py | -c code>` runs Python **inside the running editor** (Python remote execution is
  enabled locally in `Config/DefaultEngine.ini`; that line is intentionally **not committed**). The editor's
  Python globals **persist between calls**, so reset any filter variables you set (e.g. `ONLY=None`).
- `Tools/ue/bpkit.py` (import inside the editor): `ensure_var`, `ensure_fn` (function + params), `write`
  (DSL → graph, **raises** errors, unlike `BlueprintTools.write_graph_dsl` which swallows them), **`prune`** (delete
  orphaned nodes: **always prune after rewriting a graph**, because old versions are left behind), `read`, `compile_bp`,
  `save`, `set_defaults` (CDO). `Tools/ue/m1/*.py` are the M1 build scripts (good examples).
- **Unreal MCP** (`.mcp.json` → `unreal-mcp`, `http://localhost:8000/mcp`): `EditorToolset` (Blueprint/asset/
  actor tools + DSL), `UMGToolSet` (widget trees: `AddWidget`, `ToggleWidgetAsVariable`, ...; not exposed to
  editor Python, so call it via MCP), `LogsToolset`, `EditorAppToolset` (PIE).
- **Playtest:** load a level + PIE via `LevelEditorSubsystem` (`load_level`, `editor_request_begin_play`), then run
  `python Tools/ue/m1/playtest.py` (client-side; drives `PlayerPlayedCard` / `PlayerWager` and prints state).
  Screenshots with UI: console `shot showui` → `Saved/Screenshots/WindowsEditor/`.

**Blueprint DSL gotchas (learned the hard way):**
- Variables on *another* Blueprint need the full type ID: `Class|CardBP|GetIsPowerUp`, `Class|CardBP|SetIsHeld`, ...
  (the decompiler prints `|GetbIsPowerUp`, which can't be created). Find IDs with `BT.find_node_types(graph, "...")`.
- For calls to this Blueprint's own functions (`CallFunction|X`), use `:Keyword` args. A positional arg binds to the hidden `self` pin.
- **Pure nodes re-evaluate per consumer.** Cache any random/impure result in a variable (`SetTempA` ...) before
  using it twice, and cache values before you mutate what they're computed from.
- An impure function call nested inside a `return` expression **never executes**. `bind` it as a statement first.
- `%` (modulo) fails. `Utilities|IsValid` is the multi-exec macro form only. `Append` takes 2 args (nest it).
- Keyboard event nodes (`Input|KeyboardEvents|R`) can't be given bodies via DSL. Wire them with `create_node` +
  `connect_pins` (see `Player_BP` R/C/F).
- Reading a graph with `read_graph_dsl` dirties the asset (it spawns temp nodes). Don't save unrelated assets just
  because they show as unsaved.
- Don't run headless/commandlet Unreal while the editor has the project open.
