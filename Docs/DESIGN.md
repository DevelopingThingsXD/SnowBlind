# SnowBlind — Expansion Design (draft v0.2)

Status: proposal. Nothing here is locked, and the game-jam build is the starting point, not a constraint.
Goal: grow a 5-minute, luck-driven jam game into a **roguelite descent** with real decisions, captors people
remember, replayability, and a Steam demo.

v0.2 includes feedback from three player-perspective reviews (casual newcomer, roguelike veteran, Let's Play
creator). See §16 for what changed and why.

---

## 1. The hook: reading the captor in the dark

The title gives us the theme. **SnowBlind = you can't see.**

- Your **candles are your lives _and_ your light.** When one goes out you lose a life and your side of the table gets darker.
- **The core verb is reading the captor**: their tells, their bluffs, how they crack. This is what sets us apart
  from other table/captor games. Card values are just how the duel is played.
- **Winning costs you information.** Each candle the *captor* loses darkens *their* side, so their tells get harder
  to read as you get closer to winning. This stops a winning player from snowballing and keeps the end of every duel tense.
- The run is a **descent** from a snowy courtyard into darkness. Every captor down there was once a prisoner like you.

Pitch: *"Bet your candles against captors who remember you, in a card duel where every flame
that goes out makes it harder to read them."*

---

## 2. Design pillars

1. **The captors are the stars.** Personality, tells, cracking under pressure, memory. Every system should feed them.
2. **Every round is a decision, and every loss can be read.** Luck sets up the situation and the player decides.
   After a loss you always know *why*.
3. **Darkness hides the opponent, never you.** Darkness reduces information about the captor. It never hides your own
   cards or a round's result.
4. **One new idea at a time.** Systems unlock floor by floor. Floor 1 should feel as simple as War.
5. **Readable on camera.** Large final numbers, physical stakes, and dramatic pauses. Anything a viewer can't follow in a few seconds gets simplified.

---

## 3. The Descent Deck (one deck for the whole run)

- **One shared 40-card deck (1–10 ×4) persists across the whole run.** It is **not** reshuffled between floors.
  It reshuffles **only when it runs out**, announced by the Elevator Operator ("Fresh deck. Everything you
  counted is gone.").
- Because of this, **counting cards builds up over the run**: by floor 4 you know a lot about what's left. This is
  the long-term skill layer.
- **Count readout:** a large, simple display ("10s left: 1 · 9s left: 3"), shown as chalk on a slate at the table.
  Players and viewers can read it at a glance, so there's no tallying by hand. It appears from floor 2 onward.
- **Branded cards** (§7) permanently change cards in this deck. That's where builds come from.
- Both sides draw from the same deck, so **every change you make to it also helps the captor**, unless only you know
  where it is.

---

## 4. Core duel

### Kept from the jam build
Simultaneous play, higher value wins, candles as lives, the cannon fires at 0, and the AI counts cards.

### Round flow (full version, unlocked gradually; see §5)
1. **Draw** back up to 5.
2. **Play** one card face-down. Optionally attach one **Charm** (from floor 3).
3. **Wager** (from floor 2):
   - **First to act alternates** each round. Some house rules override this, so who acts first is part of the decision.
   - The first player **holds** (stake 1) or **raises** (pushes a candle forward, stake 2).
   - The responder can **call**, **fold** (lose 1), or **re-raise once** (stake 3, if they have the candles). Raising is capped at one re-raise.
   - **A fold is not a win of a raised pot.** Rewards for winning a raised pot (§8) only happen on a **revealed** win.
   - Folded cards are **shown briefly after the fold** so you learn something (and viewers get a payoff), then discarded.
4. **Items** (from the first Elevator ride on): use each item at most once per round.
5. **Reveal** (§4.2).
6. **Resolve:** the loser blows out candles equal to the stake.
7. **Tie:** both cards are buried and **the stake carries into the next round** (+1).

### 4.2 Reveal presentation (readability)
- Cards flip and **show one big final number**. Charm effects are shown as a quick transformation of that number
  (a "4" flickers into an "8"), never as on-screen arithmetic.
- **The cannon clicks one notch for each candle at stake.** At stake 3 it is visibly aimed and ready to fire. Raised pots get a
  **held beat**: a slow flip and silence before the number appears.
- **The loss summary** is a single line after each round you lose: *"His 9 beat your 7. Two 10s were still out there."* It's
  shown in the captor's voice where possible.

### 4.3 Darkness rules
- Your own cards, the final numbers, and the count slate are **always readable** (minimum emissive brightness,
  high-contrast numbers).
- What darkness reduces: **the captor's tells** (animations fade and become ambiguous), **their side of the table** (their
  items, charm count), and **ambient detail**.
- Every tell has a **visual and an audio version**, and the audio version has **optional captions** ("*knuckles crack*").

---

## 5. Onboarding: one system per floor

| Floor | New idea |
|---|---|
| 1 Courtyard | Plain War with candles. The Warden is almost impossible to lose to and **explains** his honest tells as you play |
| 2 | **Wagers** (raise/call/fold). The count slate appears |
| 3 | **Charms** |
| Elevator rides (after floor 1) | **Items** and the candle trade |
| 4 | **Branded cards** |
| 5+ | Captors start using **fake tells**; house rules get stranger |

Meta-progression can let experienced players skip ahead ("Start from floor 3", unlocked after a first clear).

---

## 6. Charms (single use, 2 per duel to start)

| Charm | Effect |
|---|---|
| ×2 | Double your own card |
| +3 / +5 | Add to your own card |
| −3 | Subtract from the **opponent's** card (min 1) |
| ÷2 | Halve the **opponent's** card (round down, min 1) |
| Frost | The opponent's charm this round fails |
| Mirror | Your card copies the opponent's final value (a guaranteed tie, so the stake carries). **Ties caused by Mirror can't be converted by any item** |

Order of effects: own charms → opponent charms → Frost cancels. The player only ever sees the final number.

---

## 7. Items and builds

### 7.1 Rules
- **Every item is tagged** as either **[Duel]** (usable once per duel) or **[Run]** (usable once per run, or passive for the run).
- You hold up to **4** items. Items come from **looting the loser** and from **the Elevator Operator** (§8).
- **No combining peeking with forcing.** Information items (peek) and forcing items (force a raise, force a re-draw) can't be used in the
  same round.

### 7.2 Archetypes
Each item belongs to one archetype, so a run develops an identity:

| Archetype | Plan |
|---|---|
| **Lowball** | Win with small cards: house rules, charms, and brands that favour low values |
| **Counter** | Know the deck better than the captor: brands, peeks, count tools |
| **Bluffer** | Win with wagers: tools for raising, folding, and controlling tells |
| **Saboteur** | Wreck the captor's card or hand: −3, ÷2, discards |

### 7.3 Branded cards (deck-shaping)
Some items **permanently brand cards in the shared deck**. The brand stays for the rest of the run (until the deck
reshuffles, if the brand says so). **Only you see your brands.** The captor plays them blind, so a brand helps whoever
plays the card, and you're the only one who knows when.

Examples: **Brand of the Ten** (all 7s count as 10 for whoever plays them), **Hollow Mark** (marked 2s count as 0;
plant them on the captor's side through a deal), **Ash Sigil** (branded cards burn after one use, thinning the deck toward what you want).

### 7.4 Starter item list (v0.2, target 20–30 at release)
| Item | Tag | Archetype | Effect |
|---|---|---|---|
| **Matchbook** | Run | — | Relight one candle. **Once per run** |
| **Hand Mirror** | Duel | Counter | Peek at the opponent's face-down card before the wager. Blocks forcing items this round |
| **Marked Card** | Run (passive) | Counter | Brand one card; you always know when it's drawn and by whom |
| **Lantern** | Duel | Counter | Cancels darkness on the captor's side for one round (tells are fully readable) |
| **Snow Globe** | Duel | Bluffer | Take your played card back and play another (before the reveal) |
| **Loaded Die** | Duel | Bluffer | Win a tie, **except ties caused by Mirror** |
| **Ice Pick** | Duel | Saboteur | Discard one random card from the captor's hand |
| **Wax Seal** | Duel | Bluffer | Your next lost wager costs 1 less (min 1) |
| **Bell** | Duel | Bluffer | The captor must raise or fold this round. **A forcing item: can't be used in a round where you peeked** |
| **Brand of the Ten** | Run | Lowball / Counter | 7s count as 10 for whoever plays them |
| **Cracked Lens** | Run (passive) | Counter | The count slate also shows how many **charms** the captor has left |

---

## 8. The Descent (run structure)

```
Courtyard → [Elevator: trade + pick next floor] → Floor → [Elevator] → … → The Bottom
```

- **Candles carry over** between floors (max 3, raised by some items). A run is a fight to keep your light.
- **No currency.** You only ever spend candles. Everything else comes from the dead.
- **Loot the loser:** when the cannon kills a captor, you take **one item of your choice** from their side of the table.
- **Winning a raised pot that was revealed** (stake 2+, not a fold) relights one of your candles (up to max) **or**
  takes one of the captor's unused charms.
- **The Elevator is the hub.** On each ride down:
  - The **Elevator Operator** (new character, a creepy shopkeeper meant for merch) offers 3 items. **Taking one costs a candle.**
    The **first trade of a run is free** and shows what the item does, so new players learn that trading is worth it.
  - **Choose the next floor from 2 options** (a cheap Slay-the-Spire-style branching path). Floors come from a pool, so runs differ.
- **Run length:** demo run 20–30 min (3 floors). Full run 45–60 min (6 floors chosen from the pool, then the Bottom).
  **Save between floors.**
- **Death:** the cannon fires. You always get something: an unlock, a lore fragment, or a new memory line for the captor (§9.5).

---

## 9. Captors

### 9.1 What a captor is made of
Each captor is a data asset made of five parts, so adding one means filling in data, not writing a new Blueprint:

| Part | Contents |
|---|---|
| **Look & story** | Mesh, animation set, voice, dialogue lines, how they ended up here |
| **House rule** | How their floor changes the rules (§10). **Every rule changes which card is good**, not just how the floor looks |
| **Personality** | `Aggression`, `BluffRate`, `CountingSkill`, `CharmGreed`, `TellHonesty` |
| **Tell pool** | 4–6 visual+audio tells that the captor draws from (§9.4) |
| **Table** | The items and charms they bring, which become your loot if you win |

### 9.2 Cracking (within a duel)
At their **last candle** each captor reaches a breaking point: personality values change sharply (calm ones become reckless,
reckless ones freeze), tells get more extreme, and the dialogue changes from threats to pleading. Combined with their side going dark,
the last round is the most tense.

### 9.3 Escalation (down the descent)
Early captors count badly and have honest tells. Deeper captors count perfectly, fake tells (from floor 5) and bring items. The Dealer
counts perfectly, bluffs about a third of the time, and copies your items.

### 9.4 Tells that must be re-learned each run
- Each run, a captor **randomly assigns** their tell pool to card strengths (for example, this run the Prisoner's
  *tremor* means a high card; next run it means a bluff). Wikis can document the pool but not the mapping.
- **A calibration reveal:** the first round against each captor is played face-up on their side, so you see one tell paired with its meaning.
- **Floor 1 (the Warden) never randomizes.** He's the tutorial, with honest tells he explains.

### 9.5 Adaptation and memory (made visible)
- **Within a run, captors adapt to your habits**: your raise frequency, how often you bluff, your fold threshold. **They always
  say so** ("You raise too much. I'm calling now."). Adaptation is something you can read and counter, never a hidden difficulty boost.
- **Across runs, captors remember you.** Track a few stats: deaths, the floor and captor that killed you, the lowest card
  you raised on, your biggest pot, the item you took most often. **15–20 lines in the demo** use them ("Back again? You raised on a three.").

### 9.6 The secret (story)
Every captor was once a prisoner who won their way down. At the Bottom the Dealer offers you his seat:
- **Take the seat:** your next run opens with **you** as the hooded Warden in the Courtyard, dealing to a new prisoner (a short
  playable scene), and then the loop continues.
- **Shoot the Dealer:** he becomes a duel you have to win, which leads to the true ending.
- **Seed it in the demo:** the Warden's hands look like the player's hands, and objects on the tables hint at earlier lives.

### 9.7 Roster
| Captor | Floor | Personality | Signature |
|---|---|---|---|
| **The Warden** (hooded) | Courtyard (fixed first) | Honest, passive, never bluffs | Teaches the game. Tells are fixed and explained. In the story, the previous winner |
| **The Prisoner** | Elevator | Nervous, raises at random, strong tells | Meme fuel: "raised on a 2 again". Desperate, because one win would make him a captor |
| **The Miner** | Mine | Patient, counts well | Works in the dark: his tells are **sounds** (tapping, coughing), captioned |
| **The Fisher** | Frozen Lake | Cautious, folds often | Brings a Hand Mirror, so he can peek too |
| **The Twins** | Catacombs | Aggressive, often re-raise | Two captors who share 3 candles and talk over each other |
| **The Bellringer** | Chapel | Theatrical bluffer | Controls when the bell tolls |
| **The Stoker** | Furnace | Greedy charm user | Burns his own items to force outcomes |
| **The Dealer** | The Bottom (fixed last) | Perfect counter, ~33% bluff | Copies your items and rotates house rules from floors you visited |

---

## 10. Floors & house rules

The rule for house rules: **each one changes which card is good.** Visual chaos is fine, but dexterity tests ("find your card") are not.

| Floor | House rule | Effect on which card is good | Built? |
|---|---|---|---|
| Courtyard | None (tutorial) | — | ✅ exists |
| Elevator Shaft | **The Lurch:** when the elevator lurches (warned by a flicker and a bell), **you and the captor swap hands.** Constant shaking is visual only | Holding onto high cards is risky; you can push weak cards onto the captor | ✅ exists |
| The Mine | **Low Ceiling:** any card above 7 counts as 7 unless it has a charm. Captor tells are sound only | Charms become essential; 10s are worth less than you'd think | ✅ exists (Cave) |
| Frozen Lake | **Thin Ice:** the lowest card each round is removed from the deck permanently | Shapes the descent deck for the rest of the run, so it ties into counting | new |
| Catacombs | **Two Mouths:** you have to beat **both** twins' cards | Middling cards lose; it's all or nothing | new |
| Chapel | **The Toll:** when the bell rings (warned one round ahead), the **lowest** card wins | A Lowball build shines; you save low cards for the toll | new |
| Furnace | **Burning Hand:** unplayed cards lose 1 value per round | Holding cards is punished; you have to play now | new |
| The Bottom | **The Dealer's Table:** rotates the house rules of floors you visited, one per round, announced | Tests everything you've learned | new |

Floors 4–7 come from a pool: you see 2 at each Elevator stop, and a full run visits 4 of them.

---

## 11. Replayability

- **Snowfall 1–10** (difficulty ladder): each level adds a modifier, such as captors starting with +1 candle, fewer
  Elevator offers, the count slate showing less, or more fake tells.
- **Unlocks** come from milestones such as reaching floor X, winning with 1 candle, or a revealed pot of 4+: new items enter the pool, along with
  starting kits ("The Gambler": 2 candles but 3 items, Bluffer archetype; "The Accountant": Counter archetype).
- **Endless "Deeper"** after the first clear: house rules stack, with a leaderboard.
- **Daily descent:** a seeded run, the same for everyone (built for creators: viewers play the same seed).
- **Lore:** fragments from each captor, collected over many runs.

---

## 12. Streaming and readability checklist

- Card numbers, final values, and the count slate are readable at 720p after compression, even at 1 candle.
- Every audio tell has a caption option, and every visual tell has an audio version.
- Big moments are physical and need no UI: the cannon notches, a candle blowout, a held beat on raised reveals, captors cracking.
- Folded cards are shown briefly.
- There are no lists of numbers or rules on screen during play; rules are explained in captor dialogue and a rules pamphlet item.
- A **streamer mode** option adds larger text and captions by default. Keep all music original so videos never get copyright claims.

---

## 13. Steam release requirements

- Main menu: continue run, new run, settings, quit. Pause menu in-game.
- Settings: resolution/fullscreen, VSync, frame cap, master/music/SFX volume, mouse sensitivity, invert Y, FOV,
  key rebinding, captions, pixelation strength (including off), brightness floor.
- Save system: mid-run save between floors, plus unlocks, stats, and captor memory.
- Steamworks: achievements, leaderboards (endless + daily), cloud saves.
- Controller support (stretch), localization-ready text (String Tables).
- Store: capsule art, ~6 screenshots, 30–60s trailer, **Next Fest demo**.

---

## 14. Technical plan (Blueprint architecture)

The jam build puts everything in `CardWar_GM`, and `OpenLevel` wipes all state between levels.

| Need | Approach |
|---|---|
| Run state: candles, items, brands, **the descent deck**, floor path, seed, adaptation stats | **`BP_RunGameInstance`** + **`SG_Run`** SaveGame |
| Cross-run state: unlocks, Snowfall level, captor memory stats, lore | **`SG_Profile`** SaveGame |
| Data-driven content | `DA_Captor` (look, personality, tell pool, house rule, dialogue, table), `DT_Items`, `DT_Charms`, `DT_Floors`, `DT_MemoryLines` |
| House rules | `BP_HouseRule` base with hooks: `OnRoundStart`, `ModifyCardValue`, `OnResolve`, `ModifyFirstToAct`, `OnLurch` |
| Items / brands | `BP_TableItem` base (`CanUse`, `Use`, `OnRoundEvent`, `Tag`, `Archetype`, `IsForcing`/`IsInfo` flags); brands stored on deck entries |
| Round flow | Replace the long Event Graph sequence in `CardWar_GM` with an explicit **round state machine** (Draw → Play → Wager → Items → Reveal → Resolve → Cleanup) using an enum and event dispatchers. Phases unlock by floor (§5) |
| Captor AI | `Opponent_BP` reads `DA_Captor`; separate functions for card choice, wager, charm, and tell output; adaptation counters; dialogue triggers |
| Tells | `BP_TellComponent`: maps strength → tell from the per-run randomized table; plays animation, audio, and caption |
| Seeded RNG | A `Random Stream` on the GameInstance (daily runs, reproducing bugs, randomizing tells) |
| Legacy cleanup | Delete the v1 `Content/Blueprints/*` system and fix up the root redirectors |

---

## 15. Roadmap

| Milestone | Contents | Exit criterion |
|---|---|---|
| **M1: Core duel** | Round state machine, draw-to-5, wagers (alternating first player, one re-raise), tie carry, reveal presentation (big number, cannon notches, held beat), loss summary line, darkness rules | One duel is fun to replay 10× in a row and every loss can be read |
| **M2: Run loop** | GameInstance + descent deck, candles carry over, loot the loser, Elevator trade (first one free) + floor choice, charms, 8–10 tagged items, Lurch + Low Ceiling rules, captor data assets, tells with calibration, visible adaptation | A full 3-floor run (20–30 min) feels like a run |
| **M3: Demo** | Floors 1–3, settings/pause/save, captions, 15–20 memory lines, the seat clue, store page, demo build | **Next Fest demo shipped; collecting wishlists** |
| **M4: Content** | Floor pool (Lake, Catacombs, Chapel, Furnace), the Dealer, brands + archetypes, 20–30 items, lore, the seat-swap and true endings | A full run completes in 45–60 min |
| **M5: Replay & release** | Snowfall 1–10, unlocks/starting kits, endless + daily, achievements, leaderboards, polish | 1.0 |

---

## 16. Review notes: what changed in v0.2 and why

| Feedback | Source | Change |
|---|---|---|
| Too many systems in the first duel; players quit during the tutorial | Newcomer, Creator | §5: one system per floor |
| Charm math is hard for viewers to follow | Creator, Newcomer | §4.2: one big final number, no arithmetic on screen |
| Losses feel random or unreadable | All three | §4.2 loss summary, folded cards shown, adaptation spoken aloud |
| Darkness and pixelation turn into a smear on stream | Creator, Veteran | §4.3: darkness hides the captor, never your cards; brightness floor; captions |
| Card counting can't matter in a 3–5 round duel | Veteran | §3: one descent deck for the whole run |
| The wager game was already solved (raise strong, never fold) | Veteran | §4: alternating first to act, one re-raise, folds never pay out a raised pot |
| Mirror + Loaded Die = guaranteed win; Hand Mirror + Bell = free pot; Matchbook "per duel" = endless lives | Veteran | §6–7: Mirror ties can't be converted; peek and force can't be combined; [Duel]/[Run] tags; Matchbook once per run |
| No build identity | Veteran | §7.2–7.3: archetypes + branded cards |
| Fixed tells get solved by wikis | Veteran | §9.4: tells re-randomized each run, with a calibration round |
| "Find your card" shaking is a dexterity tax | Newcomer, Veteran (the Creator liked the chaos) | §10: shaking is visual only; the Lurch swaps hands instead |
| Long runs with harsh deaths drive newcomers away | Newcomer | §8: 20–30 min demo runs, save between floors, a reward on every death, first trade free |
| Same floors every run | Veteran | §8/§10: choice of 2 floors at each Elevator stop, Snowfall ladder |
| Captors, memory lines, and the seat twist are the best features | All three | §9 is now a core section; memory and the seat clue are in the demo |

---

## 17. Open questions (team to decide)

1. **Wager details:** is one re-raise enough? Should folding cost 1 or the current stake?
2. **Descent deck size:** 40 cards for the whole run, or a larger "descent deck" (e.g., 60) so it lasts about 2 floors before reshuffling?
3. **Team size & timeline:** sets how many floors and items 1.0 can have.
4. **The Dealer and the story:** who started the descent, and is the true ending escape or something darker?
5. **Price & length:** suggested $5–8 for a 45–60 min run plus endless/daily.
