"""Client-side M1 smoke test: drives a running PIE session of a CardWar level through several rounds.
Run locally (NOT inside the editor):  python Tools/ue/m1/playtest.py
Requires: editor open with PIE running on Courtyard_L/Elevator_L/Cave_L, Python remote execution enabled."""
import sys, time, json
sys.path.insert(0, r"B:/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python")
import remote_execution as rx

PRELUDE = """
import unreal, json
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
gm = unreal.GameplayStatics.get_game_mode(w) if w else None
def st():
    if gm is None: return {'pie': False}
    ph = gm.get_editor_property('PlayerHand'); oh = gm.get_editor_property('OpponentHand')
    wbp = gm.get_editor_property('GeneralWBPREF')
    def txt(n):
        try: return str(wbp.get_editor_property(n).get_editor_property('text'))
        except Exception as e: return '?'
    return {'pie': True, 'round': gm.get_editor_property('RoundIndex'), 'playerFirst': gm.get_editor_property('PlayerFirst'),
            'stake': gm.get_editor_property('Stake'), 'tieCarry': gm.get_editor_property('TieCarry'),
            'wager': gm.get_editor_property('WagerState'),
            'lives': [gm.get_editor_property('PlayerLives'), gm.get_editor_property('OpponentLives')],
            'hand': [c.get_editor_property('cardValue') if not c.get_editor_property('bIsPowerUp') else 'P' for c in ph],
            'opp': [c.get_editor_property('cardValue') if not c.get_editor_property('bIsPowerUp') else 'P' for c in oh],
            'deck': len(gm.get_editor_property('initialDeck')),
            'prompt': txt('WagerPrompt_Txt'), 'summary': txt('Summary_Txt'),
            'locked': gm.get_editor_property('PlayerREF').get_editor_property('bInputLocked')}
"""

cfg = rx.RemoteExecutionConfig(); cfg.multicast_bind_address = "127.0.0.1"
r = rx.RemoteExecution(cfg); r.start()
for _ in range(30):
    if r.remote_nodes: break
    time.sleep(0.2)
r.open_command_connection(r.remote_nodes[0]["node_id"])


def run(code):
    res = r.run_command(PRELUDE + code, unattended=True, exec_mode=rx.MODE_EXEC_FILE)
    out = "".join(o.get("output", "") for o in res.get("output", []))
    if not res.get("success"):
        raise RuntimeError(res.get("result"))
    return out.strip()


def state():
    return json.loads(run("print(json.dumps(st()))").splitlines()[-1])


def play_card(index_of_number_card):
    # Mimic Player_BP.ReleaseCard: lock input, commit card, kick off the sequence.
    return run(f"""
ph = [c for c in gm.get_editor_property('PlayerHand') if not c.get_editor_property('bIsPowerUp')]
card = ph[{index_of_number_card}]
gm.call_method('PlayerPlayedCard', (card,))
print('played', card.get_editor_property('cardValue'))
""")


def wager(action):
    return run(f"gm.call_method('PlayerWager', ({action},)); print('wager', {action})")


def wait_for(pred, timeout=20.0, label=""):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = state()
        if pred(s):
            return s
        time.sleep(0.5)
    raise TimeoutError(f"timeout waiting for {label}: {s}")


log = []
try:
    s = state(); print("START", s); assert s["pie"], "PIE not running"
    plan = [1, 0, 2, 0, 1, 0, 0, 0]  # raise, hold/call, fold, ...
    last_round = 0
    for rnd, act in enumerate(plan):
        s = wait_for(lambda s: s["round"] > last_round and s["wager"] == 0 or 0 in s["lives"], 25, "round start")
        last_round = s["round"]
        if 0 in s["lives"]:
            break
        print(f"\nROUND {s['round']} first={'player' if s['playerFirst'] else 'AI'} hand={s['hand']} opp={s['opp']} deck={s['deck']} lives={s['lives']} carry={s['tieCarry']}")
        print(play_card(0))
        wait_for(lambda s: s["summary"] == "", 15, "summary cleared by BeginWager")
        s = wait_for(lambda s: s["wager"] > 0 or s["summary"] not in ("", "?"), 15, "wager or resolution")
        print("  wager state", s["wager"], "stake", s["stake"], "| prompt:", s["prompt"])
        if s["wager"] > 0:
            a = act if not (s["wager"] == 1 and act == 2) else 0  # can't fold when opening
            print(" ", wager(a))
            time.sleep(0.3)
            s2 = state()
            if s2["wager"] == 3:
                print("  AI re-raised:", repr(s2["prompt"])); print(" ", wager(0))
        s = wait_for(lambda s: s["summary"] not in ("", "?") and s["wager"] == 0, 20, "summary")
        print("  SUMMARY:", repr(s["summary"]), "| lives", s["lives"], "carry", s["tieCarry"])
        for label, text in ():
            bad = [ch for ch in text if ch.isdigit() or ch in ":[]().!,?"]
            if bad:
                print(f"  !! {label} has glyphs the HUD font can't draw: {bad}")
        log.append(s)
    print("\nFINAL", state())
finally:
    r.stop()
