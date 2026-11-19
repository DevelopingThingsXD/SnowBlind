# M1: candles are the stakes. Lost candles slide to the winner's side (no blow-out).
# Also: the player's played card turns face-up toward the player while betting.
# Run inside the editor via Tools/ue/uepy.py
import sys; sys.path.insert(0, 'B:/SnowBlind/Tools/ue')
import importlib, bpkit as K; importlib.reload(K)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT

LC = '/Game/Blueprints/v2/Blueprints/LifeCandle_BP.LifeCandle_BP'
LC_C = '/Game/Blueprints/v2/Blueprints/LifeCandle_BP.LifeCandle_BP_C'

# --- LifeCandle_BP: MoveTo + Tick glide -------------------------------------------------
lc = K.L(LC)
K.ensure_var(lc, 'MoveTarget', 'Vector')
K.ensure_var(lc, 'Moving', 'bool')
K.ensure_fn(lc, 'MoveTo', [('Target', 'Vector')])
K.compile_bp(lc)
K.write(lc, 'MoveTo', """(fn MoveTo (Target)
  (Variables|Default|SetMoveTarget Target)
  (Variables|Default|SetMoving true)
  (return))""", compile=False)
K.write(lc, 'EventGraph', """(event EventTick (DeltaSeconds)
  (if (Variables|Default|GetMoving)
    (bind target (Variables|Default|GetMoveTarget))
    (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterpTo :Current (Transformation|GetActorLocation) :Target target :DeltaTime DeltaSeconds :InterpSpeed 5.0))
    (if (< (Math|Vector|Distance(Vector) (Transformation|GetActorLocation) target) 0.05)
      (Variables|Default|SetMoving false))))""", compile=False)
for g in ('MoveTo', 'EventGraph'):
    print('LifeCandle prune', g, len(K.prune(lc, g)))
K.compile_bp(lc); K.save(lc); print('LifeCandle OK')

# --- CardWar_GM ---------------------------------------------------------------------------
gm = K.L(K.GM)
for n, t in [('PlayerCandleOrigin', 'Vector'), ('PlayerCandleStep', 'Vector'),
             ('OpponentCandleOrigin', 'Vector'), ('OpponentCandleStep', 'Vector'), ('MovingCandle', LC_C)]:
    K.ensure_var(gm, n, t)
K.ensure_fn(gm, 'InitCandleLayout')
K.ensure_fn(gm, 'LayoutCandles')
K.compile_bp(gm)

PC = '(Variables|Default|GetPlayerLifeCandles)'
OC = '(Variables|Default|GetOpponentLifeCandles)'

CODE = {}
CODE['InitCandleLayout'] = f"""(fn InitCandleLayout ()
  (bind p0 (Transformation|GetActorLocation (Utilities|Array|Get(acopy) {PC} 0)))
  (bind p1 (Transformation|GetActorLocation (Utilities|Array|Get(acopy) {PC} 1)))
  (bind o0 (Transformation|GetActorLocation (Utilities|Array|Get(acopy) {OC} 0)))
  (bind o1 (Transformation|GetActorLocation (Utilities|Array|Get(acopy) {OC} 1)))
  (Variables|Default|SetPlayerCandleOrigin p0)
  (Variables|Default|SetPlayerCandleStep (- p1 p0))
  (Variables|Default|SetOpponentCandleOrigin o0)
  (Variables|Default|SetOpponentCandleStep (- o1 o0))
  (return))"""

CODE['LayoutCandles'] = f"""(fn LayoutCandles ()
  (bind pc {PC})
  (for k (range (Utilities|Array|Length pc))
    (Class|LifeCandleBP|MoveTo (Utilities|Array|Get(acopy) pc k) :Target (+ (Variables|Default|GetPlayerCandleOrigin) (* (Variables|Default|GetPlayerCandleStep) (Math|Conversions|ToFloat(Integer) k)))))
  (bind oc {OC})
  (for k (range (Utilities|Array|Length oc))
    (Class|LifeCandleBP|MoveTo (Utilities|Array|Get(acopy) oc k) :Target (+ (Variables|Default|GetOpponentCandleOrigin) (* (Variables|Default|GetOpponentCandleStep) (Math|Conversions|ToFloat(Integer) k)))))
  (return))"""

# IsPlayer = the LOSER. Amount = candles at stake. Candles move from the loser's row to the winner's row.
CODE['LoseLives'] = f"""(fn LoseLives (IsPlayer Amount)
  (bind lives (select IsPlayer (Variables|Default|GetPlayerLives) (Variables|Default|GetOpponentLives)))
  (Variables|Default|SetTempA (Math|Integer|Min(Integer) Amount lives))
  (for _ (range (Variables|Default|GetTempA))
    (if IsPlayer
      (bind pc {PC})
      (if (> (Utilities|Array|Length pc) 0)
        (Variables|Default|SetMovingCandle (Utilities|Array|Get(acopy) pc (- (Utilities|Array|Length pc) 1)))
        (Utilities|Array|RemoveItem pc (Variables|Default|GetMovingCandle))
        (Utilities|Array|Add {OC} (Variables|Default|GetMovingCandle)))
      (else
        (bind oc {OC})
        (if (> (Utilities|Array|Length oc) 0)
          (Variables|Default|SetMovingCandle (Utilities|Array|Get(acopy) oc (- (Utilities|Array|Length oc) 1)))
          (Utilities|Array|RemoveItem oc (Variables|Default|GetMovingCandle))
          (Utilities|Array|Add {PC} (Variables|Default|GetMovingCandle))))))
  (Variables|Default|SetPlayerLives (Utilities|Array|Length {PC}))
  (Variables|Default|SetOpponentLives (Utilities|Array|Length {OC}))
  (CallFunction|LayoutCandles)
  (Audio|PlaySound2D "/Game/Audio/SE/ChainRattling.ChainRattling" 0.35)
  (bind left (select IsPlayer (Variables|Default|GetPlayerLives) (Variables|Default|GetOpponentLives)))
  (Class|CannonBP|LookAt (Variables|Default|GetCannonREF) IsPlayer (== left 0) (not IsPlayer))
  (return))"""

CODE['PlayerPlayedCard'] = """(fn PlayerPlayedCard (HeldCard)
  (Variables|Default|SetPlayerCommittedCard HeldCard)
  (Class|CardBP|SetTargetRelativeRotation "90.000000,180.000000,0.000000" HeldCard)
  (CallFunction|CardPlay_Sequence)
  (return))"""

for name, code in CODE.items():
    try:
        K.write(gm, name, code, compile=False); print('OK', name)
    except Exception as e:
        print('ERR', name, repr(e)[:800])
for name in CODE:
    print('prune', name, len(K.prune(gm, name)))
try:
    K.compile_bp(gm); K.save(gm); print('GM COMPILED+SAVED')
except Exception as e:
    print('COMPILE ERR', str(e)[:3000])
