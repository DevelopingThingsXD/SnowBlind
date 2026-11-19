# M1: base stake BURNS (candle extinguished, stays as a dark stub on the loser's side);
# RAISED candles TRANSFER to the winner (stay lit). Folding burns 1.
# Layout: max 4 per row; candles 5-6 go in a staggered second row offset toward the player.
# Run inside the editor:  python Tools/ue/uepy.py -c "exec(open('B:/SnowBlind/Tools/ue/m1/candles2.py',encoding='utf-8').read())"
import sys; sys.path.insert(0, 'B:/SnowBlind/Tools/ue')
import importlib, bpkit as K; importlib.reload(K)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT

LC_C = '/Game/Blueprints/v2/Blueprints/LifeCandle_BP.LifeCandle_BP_C'
gm = K.L(K.GM)
K.ensure_var(gm, 'PlayerDeadCandles', LC_C, True)
K.ensure_var(gm, 'OpponentDeadCandles', LC_C, True)
K.ensure_var(gm, 'CandleRowOffset', 'Vector')
K.ensure_var(gm, 'BaseStake', 'int')
K.ensure_fn(gm, 'SlotPos', [('IsPlayer', 'bool'), ('K', 'int')], [('Pos', 'Vector')])
K.ensure_fn(gm, 'PayStake', [('LoserIsPlayer', 'bool'), ('Burn', 'int'), ('Give', 'int')])
K.compile_bp(gm)

PC = '(Variables|Default|GetPlayerLifeCandles)'
OC = '(Variables|Default|GetOpponentLifeCandles)'
PD = '(Variables|Default|GetPlayerDeadCandles)'
OD = '(Variables|Default|GetOpponentDeadCandles)'

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
  (bind perp (Math|Vector|CrossProduct (- p1 p0) (Math|Vector|MakeVector 0.0 0.0 1.0)))
  (bind toPlayer (- (Transformation|GetActorLocation (Variables|Default|GetPlayerREF)) p0))
  (Variables|Default|SetCandleRowOffset (select (< (Math|Vector|DotProduct perp toPlayer) 0.0) (* perp -1.0) perp))
  (return))"""

# slot k: row = k>=4 ? 1 : 0 ; col = k - 4*row ; second row is staggered half a step and offset toward the player
CODE['SlotPos'] = """(fn SlotPos (IsPlayer K)
  (bind row (select (>= K 4) 1 0))
  (bind col (- K (* row 4)))
  (bind origin (select IsPlayer (Variables|Default|GetPlayerCandleOrigin) (Variables|Default|GetOpponentCandleOrigin)))
  (bind step (select IsPlayer (Variables|Default|GetPlayerCandleStep) (Variables|Default|GetOpponentCandleStep)))
  (bind rowf (Math|Conversions|ToFloat(Integer) row))
  (return (+ (+ origin (* step (+ (Math|Conversions|ToFloat(Integer) col) (* 0.5 rowf)))) (* (Variables|Default|GetCandleRowOffset) rowf))))"""

CODE['LayoutCandles'] = f"""(fn LayoutCandles ()
  (bind pc {PC})
  (bind pd {PD})
  (bind oc {OC})
  (bind od {OD})
  (for k (range (Utilities|Array|Length pc))
    (bind pos (CallFunction|SlotPos :IsPlayer true :K k))
    (Class|LifeCandleBP|MoveTo (Utilities|Array|Get(acopy) pc k) :Target pos))
  (for k (range (Utilities|Array|Length pd))
    (bind pos (CallFunction|SlotPos :IsPlayer true :K (+ k (Utilities|Array|Length pc))))
    (Class|LifeCandleBP|MoveTo (Utilities|Array|Get(acopy) pd k) :Target pos))
  (for k (range (Utilities|Array|Length oc))
    (bind pos (CallFunction|SlotPos :IsPlayer false :K k))
    (Class|LifeCandleBP|MoveTo (Utilities|Array|Get(acopy) oc k) :Target pos))
  (for k (range (Utilities|Array|Length od))
    (bind pos (CallFunction|SlotPos :IsPlayer false :K (+ k (Utilities|Array|Length oc))))
    (Class|LifeCandleBP|MoveTo (Utilities|Array|Get(acopy) od k) :Target pos))
  (return))"""

CODE['PayStake'] = f"""(fn PayStake (LoserIsPlayer Burn Give)
  (Variables|Default|SetTempA (Math|Integer|Min(Integer) Burn (select LoserIsPlayer (Variables|Default|GetPlayerLives) (Variables|Default|GetOpponentLives))))
  (for _ (range (Variables|Default|GetTempA))
    (if LoserIsPlayer
      (bind pc {PC})
      (if (> (Utilities|Array|Length pc) 0)
        (Variables|Default|SetMovingCandle (Utilities|Array|Get(acopy) pc (- (Utilities|Array|Length pc) 1)))
        (Utilities|Array|RemoveItem pc (Variables|Default|GetMovingCandle))
        (Utilities|Array|Add {PD} (Variables|Default|GetMovingCandle))
        (Class|LifeCandleBP|BlowOutCandle (Variables|Default|GetMovingCandle)))
      (else
        (bind oc {OC})
        (if (> (Utilities|Array|Length oc) 0)
          (Variables|Default|SetMovingCandle (Utilities|Array|Get(acopy) oc (- (Utilities|Array|Length oc) 1)))
          (Utilities|Array|RemoveItem oc (Variables|Default|GetMovingCandle))
          (Utilities|Array|Add {OD} (Variables|Default|GetMovingCandle))
          (Class|LifeCandleBP|BlowOutCandle (Variables|Default|GetMovingCandle))))))
  (Variables|Default|SetTempB (Math|Integer|Min(Integer) Give (Utilities|Array|Length (select LoserIsPlayer {PC} {OC}))))
  (for _ (range (Variables|Default|GetTempB))
    (if LoserIsPlayer
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
  (if (> (Variables|Default|GetTempB) 0)
    (Audio|PlaySound2D "/Game/Audio/SE/ChainRattling.ChainRattling" 0.35))
  (bind left (select LoserIsPlayer (Variables|Default|GetPlayerLives) (Variables|Default|GetOpponentLives)))
  (Class|CannonBP|LookAt (Variables|Default|GetCannonREF) LoserIsPlayer (== left 0) (not LoserIsPlayer))
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
