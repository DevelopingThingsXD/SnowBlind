# SnowBlind — project map

Blueprint-only Unreal Engine **5.8** project (no C++ / no `Source/`). Upgraded from 5.6 on 2026-11-18;
most assets are still saved as 5.6 and upgrade on load. Engine install: `B:\UE_5.8`.

**The game:** a first-person, seated, high-stakes card duel ("CardWar"). You sit at a table across from a
captor/opponent. Each round both sides play one numbered card, the higher value wins, the loser loses a
life (a candle is blown out). Lose all 3 and a cannon turns and shoots you. Win and you move to the next
location. Three locations: Courtyard (1) → Elevator (2) → Cave (3) → back to Main Menu.

**Direction:** the jam build is being expanded into a roguelite "descent" (more floors, wagers, items,
house rules, Steam demo). Proposal and roadmap: [Docs/DESIGN.md](Docs/DESIGN.md). The rules below
describe what's **currently implemented**, not the target design.

## Rules (as implemented — source: `CardWar_GM`, `Opponent_BP`, `Card_BP`)

- **Deck:** one shared 40-card deck: values 1–10, four of each (`CardWar_GM.Initial Deck`). Draws remove
  from it (no replacement).
- **Hands:** each side is dealt **5 number cards** + **2 power-up cards**.
- **Power-ups** drawn at random from `Power Up Deck` map: **×2 (Multiply)**, **+5 (Add)**, **+3 (Add)**.
  `PowerUpType_Enum` also defines Subtract/Divide but they aren't in the deck. A power-up applied to a
  card sets `Card_BP.modifiedValue` (card shows chains/overlay); comparison uses `modifiedValue` when set,
  otherwise `cardValue`.
- **Round:** player drags a card into the play area (`PlayArea_Player_BP`) → `PlayerPlayedCard` →
  opponent responds (`OpponentPlayCard`) → both cards are presented/flipped (`PresentCards`) →
  higher value wins → loser's lives −1, `BlowoutCandle` → played cards destroyed, hands re-fanned.
- **Tie:** prints "TIE", then one card's value is randomly nudged by ±1–3 (clamped 1–100) to break it.
- **Lives:** 3 each (`Player Lives`, `Opponent Lives`), shown as 6 `LifeCandle_BP` actors in the level
  (indices 0–2 player, 3–5 opponent; `AssignLifeCandles`).
- **Game over:** `Cannon_BP.LookAt` swivels to the loser → `ShootLoser` → `General_WBP.GameOver` shows
  "You Win"/"You Lose" + cannon blast SFX → `Open Level` by current level name.
- **Opponent AI** (`Opponent_BP.PlayCard`): tracks the average of the cards still unseen
  (`UpdateCardCountAverage`, `Remaining Card Average`); compares its chosen card to that average to decide
  whether to spend a power-up; macro `ChoosePowerUpDeck` prefers ×2 on cards **≥ 6** and +N on lower cards,
  falling back to whichever power-up pile isn't empty.
- `Power Up Spawn Chance = 5` (1/X) exists on the GM but is currently **unused** by any graph.

## Controls (`Content/Inputs/IMC_User`, handled in `Player_BP`)

Mouse look (clamped: yaw ±50, pitch −20..5, sensitivity 0.75) • **Left click/drag** number cards into the
play area • **Right click** power-up cards to apply to a card • **Hold Space** = freelook. Input is locked
(`bInputLocked`) while a round resolves. Frame rate capped to 120 (`CapFramerate`).

## Level flow

| Map | Game mode | Notes |
|---|---|---|
| `Levels/MainMenu_L` (startup + editor default) | `MainMenu_GM` + `MainMenu_Pawn_BP` | 3D menu cards (`MainMenuCard_BP`): Play → `Courtyard_L`, Quit |
| `Levels/Courtyard_L` — level 1 | project default `CardWar_GM` | snowy temple courtyard, braziers, wind/snow FX; opponent = hooded figure |
| `Levels/Elevator_L` — level 2 | `CardWar_GM` | moving elevator shaft, `ElevatorCameraShake_CS`; prisoner opponent |
| `Levels/Cave_L` — level 3 (final) | `CardWar_GM` | mine cave (minecart, crane, gemstones, water drips), chain splines; prisoner opponent; win → MainMenu |
| `TestLevel_v2_L`, `Basic_L`, `TestLevel` | — | test/scratch maps |

Next-level routing lives in `Blueprints/v2/UI/General_WBP` (Switch on current level name → `Open Level`).

## Where things live

- **`Content/Blueprints/v2/`** — ⭐ the live game. Everything above is here.
  - `Blueprints/CardWar_GM` — GameModeBase. Owns deck, hands, lives, round flow, win/lose, spawning cards.
  - `Blueprints/Player_BP` — Pawn: camera, hover line-trace, pickup/release/drag, power-up application, hand light/Niagara.
  - `Blueprints/Opponent_BP` — AI opponent actor (skeletal mesh, hand slots, AI card/power-up choice).
  - `Blueprints/Card_BP` — a card: value, modifiedValue, power-up data, state machine
    (`CardState_Enum`: IdleInHand, Hovered, Dragging, Played, Resolved), fan positioning, chains, text.
  - `Cannon_BP`, `LifeCandle_BP`, `PlayArea_Player_BP`, `ChainSpline_BP`, `TextRenderCardValue_BP` (big floating value number at reveal).
  - `MainMenu/` — menu GM, pawn, menu cards. `UI/General_WBP` (HUD, game over, "Hold Space to Freelook"), `UI/MainMenu_UI`.
- **`Content/Blueprints/*.uasset` (v1)** — **legacy, unused by any game level**: old interaction system
  (`AC_InteractionTrace`, `BPI_Interaction`, `BP_User`), tie wheel (`BP_TieWheel`, `BP_TieBreakerManager`,
  `WBP_TieBreaker`), `E_Difficulty` (Easy/Medium/Hard), `E_CardSide` (Player/Dealer). Only `TestLevel` uses them.
- **`Content/BP_*.uasset` + `NewBlueprint`** (root, ~2 KB each) — **redirectors** left from moves. Fix up redirectors before deleting.
- `Content/Art/` — meshes/materials/textures; `Cards/` (Card_1..10 MIs, chains/lock/overlay mats),
  `Characters/` (HoodedFigure, Prisoner_1, Prisoner_2 — Mixamo-rigged), `Hand/` (first-person hand anims:
  Idle/HoverCards/HoldCards/Powerup), `ParticleSystems/` (snow, wind-snow, cold breath, candle smoke, fire,
  glowing number), `PostProcess/` (`PPM_ResolutionLimiter` — used in every level; `PPM_8BitColor` — unused).
- `Content/Audio/` — BGM (Courtyard, Cave, Elevator), BGS ambience, SE (cannon blast, card hover, chains, gun adjust).
- `Content/Fonts/` — CS Aspen Drawn (hand-drawn display font).

## Art direction (observed)

Lo-fi retro 3D horror: low internal resolution via post-process resolution limiter, hand-painted textures,
moody fog, warm firelight (braziers, candles) against cold snow/moon/stars, emissive glowing card numbers,
chains on powered-up cards, hand-drawn font. Prisoner/captor framing: you gamble for your life.

## Rendering / project settings

Forward-ish legacy look: Lumen off (`DynamicGlobalIlluminationMethod=0`, `ReflectionMethod=0`), Nanite off,
VSM off, static lighting allowed, no AA (`AntiAliasingMethod=0`), auto-exposure off, DX12 SM6.

## Working on this project with Claude

- **Read Blueprints without the editor:** `python Tools/bp_index.py` → `Saved/BlueprintIndex/*.txt`
  (variables + defaults, components, every graph's nodes and literal pin values; no wire order).
  Re-run after Blueprint changes. Never `Read`/`Edit` `.uasset`/`.umap` directly — they're binary.
- **Unreal MCP** (`.mcp.json` → `unreal-mcp` at `http://localhost:8000/mcp`): plugin `ModelContextProtocol`
  auto-starts with the editor (`Config/DefaultEditorPerProjectUserSettings.ini`). Currently only the
  `AgentSkillToolset` is exposed. For live Blueprint/actor/property access enable **`EditorToolset`**
  (and e.g. `UMGToolSet`) in `SnowBlind.uproject`, then restart the editor.
- Don't run headless/commandlet Unreal while the editor has the project open.
