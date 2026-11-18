# M1: wager + round flow on CardWar_GM (run inside editor via Tools/ue/uepy.py)
import sys; sys.path.insert(0, 'B:/SnowBlind/Tools/ue')
import importlib, bpkit as K; importlib.reload(K)

gm = K.L(K.GM)


def cat(*parts):
    """Nested String Append. Bare ints/exprs wrapped with i() become ToString(Integer)."""
    expr = parts[0]
    for p in parts[1:]:
        expr = f'(Utilities|String|Append {expr} {p})'
    return expr


def i(expr):
    return f'(Utilities|String|ToString(Integer) {expr})'


def q(s):
    return '"' + s + '"'


STAKE = '(Variables|Default|GetStake)'
PLIVES = '(Variables|Default|GetPlayerLives)'
OLIVES = '(Variables|Default|GetOpponentLives)'
OPP = '(Variables|Default|GetOpponentREF)'
OCARD = '(Variables|Default|GetPendingOpponentCard)'
PCARD = '(Variables|Default|GetPendingPlayerCard)'


def ai_decide(facing, allow):
    return (f'(Class|OpponentBP|DecideWager :self {OPP} :FacingRaise {facing} :AllowRaise {allow} '
            f':CardValue (CallFunction|FinalValue :Card {OCARD}) :UnseenAverage (CallFunction|OpponentUnseenAverage))')


PROMPT_OPEN = cat(q('Stake: '), i(STAKE), q('    [R] Raise    [C] Hold'))
PROMPT_OPEN_NORAISE = cat(q('Stake: '), i(STAKE), q('    [C] Hold'))
PROMPT_FACING = cat(q('He pushes a candle forward. Stake: '), i(STAKE), q('    [C] Call    [F] Fold    [R] Re-raise'))
PROMPT_FACING_NORAISE = cat(q('He pushes a candle forward. Stake: '), i(STAKE), q('    [C] Call    [F] Fold'))
PROMPT_RERAISED = cat(q('He raises again! Stake: '), i(STAKE), q('    [C] Call    [F] Fold'))

FLIP = """
  (Class|CardBP|SetTargetRelativeRotation "90.000000,180.000000,0.000000" pc)
  (Class|CardBP|SetTargetRelativeRotation "90.000000,180.000000,0.000000" oc)
  (Audio|PlaySound2D "/Game/Audio/SE/CardHover_1_Cue.CardHover_1_Cue")
  (Utilities|FlowControl|Delay 0.2)
  (Audio|PlaySound2D "/Game/Audio/SE/CardHover_1_Cue.CardHover_1_Cue")
  (CallFunction|SpawnCardNumbers)"""

FUNCS = {}
FUNCS['DestroyPlayerPowerUp'] = """(fn DestroyPlayerPowerUp ()
  (bind player (Variables|Default|GetPlayerREF))
  (bind ap (Class|PlayerBP|GetAppliedPowerUp player))
  (Utilities|IsValid ap
    (:"Is Valid"
      (Utilities|Array|RemoveItem (Variables|Default|GetPlayerHand) ap)
      (Actor|DestroyActor ap)
      (Class|PlayerBP|SetAppliedPowerUp :self player)
      (return))
    (:"Is Not Valid"
      (return))))"""

FUNCS['DestroyOpponentPowerUp'] = """(fn DestroyOpponentPowerUp ()
  (bind op (Variables|Default|GetPendingOppPowerUp))
  (Utilities|IsValid op
    (:"Is Valid"
      (Utilities|Array|RemoveItem (Variables|Default|GetOpponentHand) op)
      (Actor|DestroyActor op)
      (Variables|Default|SetPendingOppPowerUp)
      (return))
    (:"Is Not Valid"
      (return))))"""

FUNCS['PlayerWager'] = f"""(fn PlayerWager (Action)
  (bind state (Variables|Default|GetWagerState))
  (if (== state 1)
    (if (and (== Action 1) (> {PLIVES} {STAKE}))
      (Variables|Default|SetStake (+ {STAKE} 1))
      (CallFunction|CannonNotch)
      (bind ai {ai_decide('true', f'(> {OLIVES} {STAKE})')})
      (if (== ai 1)
        (Variables|Default|SetStake (+ {STAKE} 1))
        (Variables|Default|SetReRaiseUsed true)
        (CallFunction|CannonNotch)
        (Variables|Default|SetWagerState 3)
        (CallFunction|ShowPrompt :Msg {PROMPT_RERAISED})
        (elif (== ai 2)
          (Variables|Default|SetFoldByPlayer false)
          (CallFunction|FoldRound)
          (else
            (CallFunction|RevealRound))))
      (elif (== Action 0)
        (CallFunction|RevealRound)))
    (elif (== state 2)
      (if (== Action 0)
        (CallFunction|RevealRound)
        (elif (== Action 2)
          (Variables|Default|SetFoldByPlayer true)
          (CallFunction|FoldRound)
          (elif (and (== Action 1) (> {PLIVES} {STAKE}))
            (Variables|Default|SetStake (+ {STAKE} 1))
            (Variables|Default|SetReRaiseUsed true)
            (CallFunction|CannonNotch)
            (bind ai2 {ai_decide('true', 'false')})
            (if (== ai2 2)
              (Variables|Default|SetFoldByPlayer false)
              (CallFunction|FoldRound)
              (else
                (CallFunction|RevealRound))))))
      (elif (== state 3)
        (if (== Action 0)
          (CallFunction|RevealRound)
          (elif (== Action 2)
            (Variables|Default|SetFoldByPlayer true)
            (CallFunction|FoldRound)))))))"""

EVENTS = {}
EVENTS['StartRound'] = f"""(event Custom|StartRound
  (Variables|Default|SetRoundIndex (+ (Variables|Default|GetRoundIndex) 1))
  (Variables|Default|SetWagerState 0)
  (Variables|Default|SetPlayerFirst (not (Variables|Default|GetPlayerFirst)))
  (CallFunction|DrawToFive)
  (CallFunction|ShowPrompt :Msg "")
  (Class|OpponentBP|SetRemainingCardAverage (CallFunction|OpponentUnseenAverage) {OPP})
  (Class|PlayerBP|SetInputLocked false (Variables|Default|GetPlayerREF)))"""

EVENTS['BeginWager'] = f"""(event Custom|BeginWager
  (CallFunction|ShowSummary :Msg "")
  (Variables|Default|SetStake (+ 1 (Variables|Default|GetTieCarry)))
  (Variables|Default|SetReRaiseUsed false)
  (if (> {STAKE} 1)
    (CallFunction|CannonNotch))
  (if (Variables|Default|GetPlayerFirst)
    (Variables|Default|SetWagerState 1)
    (if (> {PLIVES} {STAKE})
      (CallFunction|ShowPrompt :Msg {PROMPT_OPEN})
      (else
        (CallFunction|ShowPrompt :Msg {PROMPT_OPEN_NORAISE})))
    (else
      (CallFunction|ShowPrompt :Msg "He studies his card...")
      (Utilities|FlowControl|Delay 1.0)
      (bind ai {ai_decide('false', f'(> {OLIVES} {STAKE})')})
      (if (== ai 1)
        (Variables|Default|SetStake (+ {STAKE} 1))
        (CallFunction|CannonNotch)
        (Variables|Default|SetWagerState 2)
        (if (> {PLIVES} {STAKE})
          (CallFunction|ShowPrompt :Msg {PROMPT_FACING})
          (else
            (CallFunction|ShowPrompt :Msg {PROMPT_FACING_NORAISE})))
        (else
          (CallFunction|RevealRound))))))"""

EVENTS['RevealRound'] = f"""(event Custom|RevealRound
  (Variables|Default|SetWagerState 0)
  (CallFunction|ShowPrompt :Msg "")
  (bind pc {PCARD})
  (bind oc {OCARD})
  (if (> {STAKE} 1)
    (Utilities|FlowControl|Delay 1.2)){FLIP}
  (Utilities|FlowControl|Delay 1.5)
  (Variables|Default|SetTempA (CallFunction|FinalValue :Card pc))
  (Variables|Default|SetTempB (CallFunction|FinalValue :Card oc))
  (bind pv (Variables|Default|GetTempA))
  (bind ov (Variables|Default|GetTempB))
  (if (== pv ov)
    (Variables|Default|SetTieCarry (+ (Variables|Default|GetTieCarry) 1))
    (CallFunction|ShowSummary :Msg {cat(q('A tie at '), i('pv'), q('. Both cards are buried. Next round starts at '), i('(+ 1 (Variables|Default|GetTieCarry))'), q(' candles.'))})
    (elif (> pv ov)
      (Variables|Default|SetTieCarry 0)
      (CallFunction|ShowSummary :Msg {cat(q('Your '), i('pv'), q(' beat his '), i('ov'), q('. He loses '), i(STAKE), q(' candle(s).'))})
      (CallFunction|LoseLives :IsPlayer false :Amount {STAKE})
      (else
        (Variables|Default|SetTieCarry 0)
        (CallFunction|ShowSummary :Msg {cat(q('His '), i('ov'), q(' beat your '), i('pv'), q('. You lose '), i(STAKE), q(' candle(s). '), i('(CallFunction|CountHigherInDeck :Value pv)'), q(' higher cards were still in the deck.'))})
        (CallFunction|LoseLives :IsPlayer true :Amount {STAKE}))))
  (CallFunction|CleanupRound))"""

EVENTS['FoldRound'] = f"""(event Custom|FoldRound
  (Variables|Default|SetWagerState 0)
  (CallFunction|ShowPrompt :Msg "")
  (bind pc {PCARD})
  (bind oc {OCARD}){FLIP}
  (Utilities|FlowControl|Delay 1.5)
  (Variables|Default|SetTieCarry 0)
  (Variables|Default|SetTempA (CallFunction|FinalValue :Card pc))
  (Variables|Default|SetTempB (CallFunction|FinalValue :Card oc))
  (if (Variables|Default|GetFoldByPlayer)
    (CallFunction|ShowSummary :Msg {cat(q('You folded. His card was a '), i('(Variables|Default|GetTempB)'), q('.'))})
    (CallFunction|LoseLives :IsPlayer true :Amount 1)
    (else
      (CallFunction|ShowSummary :Msg {cat(q('He folded his '), i('(Variables|Default|GetTempB)'), q('. Your '), i('(Variables|Default|GetTempA)'), q(' takes a candle.'))})
      (CallFunction|LoseLives :IsPlayer false :Amount 1)))
  (CallFunction|CleanupRound))"""

EVENTS['CleanupRound'] = f"""(event Custom|CleanupRound
  (bind pc {PCARD})
  (bind oc {OCARD})
  (Utilities|Array|RemoveItem (Variables|Default|GetPlayerHand) pc)
  (Utilities|Array|RemoveItem (Variables|Default|GetOpponentHand) oc)
  (Actor|DestroyActor pc)
  (Actor|DestroyActor oc)
  (CallFunction|DestroyPlayerPowerUp)
  (CallFunction|DestroyOpponentPowerUp)
  (CallFunction|RefreshCardLocations)
  (Class|PlayerBP|RefreshLocalHandRefs (Variables|Default|GetPlayerREF))
  (if (and (> {PLIVES} 0) (> {OLIVES} 0))
    (Utilities|FlowControl|Delay 1.5)
    (CallFunction|StartRound)))"""

K.ensure_var(gm, 'PlayerFirst', 'bool')
K.ensure_fn(gm, 'DestroyPlayerPowerUp')
K.ensure_fn(gm, 'DestroyOpponentPowerUp')
K.compile_bp(gm)

only = globals().get('ONLY')
for name, code in FUNCS.items():
    if only and name not in only:
        continue
    try:
        K.write(gm, name, code, compile=False); print('OK fn', name)
    except Exception as e:
        print('ERR fn', name, repr(e)[:800])
for name, code in EVENTS.items():
    if only and name not in only:
        continue
    try:
        K.write(gm, 'EventGraph', code, compile=False); print('OK ev', name)
    except Exception as e:
        print('ERR ev', name, repr(e)[:800])
try:
    K.compile_bp(gm); print('COMPILED')
except Exception as e:
    print('COMPILE ERR', str(e)[:4000])
