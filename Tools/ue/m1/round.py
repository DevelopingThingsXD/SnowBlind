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


def W(expr):
    """Number as digits (HUD uses Roboto now; NumberWord kept for the blackletter font)."""
    return i(expr)


def CN(expr):
    """'1 candle' / '3 candles' (pure nodes only, safe inside select)."""
    return cat(i(expr), f'(select (== {expr} 1) " candle" " candles")')


NL = chr(10)
BASE = '(Variables|Default|GetBaseStake)'
GIVE = f'(- {STAKE} {BASE})'
STAKE_TEXT = cat(q('Loser burns '), CN(BASE), f'(select (> {GIVE} 0) {cat(q(" and hands over "), i(GIVE))} "")')
PROMPT_OPEN = cat(STAKE_TEXT, q('        [R] Raise        [C] Hold'))
PROMPT_OPEN_NORAISE = cat(STAKE_TEXT, q('        [C] Hold'))
PROMPT_FACING = cat(q('He pushes a candle forward' + NL), STAKE_TEXT, q('        [C] Call        [F] Fold        [R] Raise again'))
PROMPT_FACING_NORAISE = cat(q('He pushes a candle forward' + NL), STAKE_TEXT, q('        [C] Call        [F] Fold'))
PROMPT_RERAISED = cat(q('He raises again' + NL), STAKE_TEXT, q('        [C] Call        [F] Fold'))
BURN_HIS = f'(select (== {BASE} 1) "His candle goes out" {cat(i(BASE), q(" of his candles go out"))})'
BURN_YOUR = f'(select (== {BASE} 1) "Your candle goes out" {cat(i(BASE), q(" of your candles go out"))})'
GIVE_TO_YOU = f'(Math|Integer|Min(Integer) {GIVE} (- {OLIVES} {BASE}))'
GIVE_TO_HIM = f'(Math|Integer|Min(Integer) {GIVE} (- {PLIVES} {BASE}))'
GIVE_YOU = f'(select (> {GIVE_TO_YOU} 0) {cat(q(NL + "You take "), CN(GIVE_TO_YOU))} "")'
GIVE_HE = f'(select (> {GIVE_TO_HIM} 0) {cat(q(NL + "He takes "), CN(GIVE_TO_HIM))} "")'

FLIP = """
  (Class|CardBP|SetTargetRelativeRotation "90.000000,180.000000,0.000000" pc)
  (Class|CardBP|SetTargetRelativeRotation "90.000000,180.000000,0.000000" oc)
  (Audio|PlaySound2D "/Game/Audio/SE/CardHover_1_Cue.CardHover_1_Cue")
  (Utilities|FlowControl|Delay 0.2)
  (Audio|PlaySound2D "/Game/Audio/SE/CardHover_1_Cue.CardHover_1_Cue")
  (CallFunction|SpawnCardNumbers)"""

FUNCS = {}
FUNCS['NumberWord'] = """(fn NumberWord (N)
  (return (Utilities|Array|Get(acopy) (Variables|Default|GetNumberWords) (Math|Integer|Clamp(Integer) N 0 30))))"""
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
  (if (== (Variables|Default|GetRoundIndex) 1)
    (CallFunction|InitCandleLayout))
  (Variables|Default|SetWagerState 0)
  (Variables|Default|SetPlayerFirst (not (Variables|Default|GetPlayerFirst)))
  (CallFunction|DrawToFive)
  (CallFunction|ShowPrompt :Msg "")
  (Class|OpponentBP|SetRemainingCardAverage (CallFunction|OpponentUnseenAverage) {OPP})
  (Class|PlayerBP|SetInputLocked false (Variables|Default|GetPlayerREF)))"""

EVENTS['BeginWager'] = f"""(event Custom|BeginWager
  (CallFunction|ShowSummary :Msg "")
  (Variables|Default|SetStake (+ 1 (Variables|Default|GetTieCarry)))
  (Variables|Default|SetBaseStake (Variables|Default|GetStake))
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
      (CallFunction|ShowPrompt :Msg "He studies his card")
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
    (CallFunction|ShowSummary :Msg {cat(q('A tie at '), W('pv'), q(NL + 'Both cards are buried' + NL + 'Next round the loser burns '), CN('(+ 1 (Variables|Default|GetTieCarry))'))})
    (elif (> pv ov)
      (Variables|Default|SetTieCarry 0)
      (CallFunction|ShowSummary :Msg {cat(q('Your '), W('pv'), q(' beat his '), W('ov'), q(NL), BURN_HIS, GIVE_YOU)})
      (CallFunction|PayStake :LoserIsPlayer false :Burn {BASE} :Give {GIVE})
      (else
        (Variables|Default|SetTieCarry 0)
        (CallFunction|ShowSummary :Msg {cat(q('His '), W('ov'), q(' beat your '), W('pv'), q(NL), BURN_YOUR, GIVE_HE, q(NL + 'There were still '), W('(CallFunction|CountHigherInDeck :Value pv)'), q(' higher cards in the deck'))})
        (CallFunction|PayStake :LoserIsPlayer true :Burn {BASE} :Give {GIVE}))))
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
    (CallFunction|ShowSummary :Msg {cat(q('You folded' + NL + 'His card was '), W('(Variables|Default|GetTempB)'), q(NL + 'Your candle goes out'))})
    (CallFunction|PayStake :LoserIsPlayer true :Burn 1 :Give 0)
    (else
      (CallFunction|ShowSummary :Msg {cat(q('He folded his '), W('(Variables|Default|GetTempB)'), q(NL + 'His candle goes out'))})
      (CallFunction|PayStake :LoserIsPlayer false :Burn 1 :Give 0)))
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
K.ensure_var(gm, 'NumberWords', 'string', True)
K.ensure_fn(gm, 'NumberWord', [('N', 'int')], [('Word', 'string')])
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
WORDS = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','twenty one','twenty two','twenty three','twenty four','twenty five','twenty six','twenty seven','twenty eight','twenty nine','thirty']
try:
    K.compile_bp(gm); K.set_defaults(gm, {'NumberWords': WORDS}); K.compile_bp(gm); K.save(gm); print('COMPILED+SAVED')
except Exception as e:
    print('COMPILE ERR', str(e)[:4000])
