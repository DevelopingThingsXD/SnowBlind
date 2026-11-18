# M1: helper functions on CardWar_GM (run inside editor via Tools/ue/uepy.py)
import sys; sys.path.insert(0, 'B:/SnowBlind/Tools/ue')
import importlib, bpkit as K; importlib.reload(K)

gm = K.L(K.GM)
for n, t, arr in [('TempCount', 'int', False), ('TempFloat', 'float', False),
                  ('TempCards', K.CARD_C, True), ('FoldByPlayer', 'bool', False),
                  ('TempA', 'int', False), ('TempB', 'int', False), ('PickedCard', K.CARD_C, False)]:
    K.ensure_var(gm, n, t, arr)

K.ensure_fn(gm, 'FinalValue', [('Card', K.CARD_C)], [('Value', 'int')])
K.ensure_fn(gm, 'RefillDeck')
K.ensure_fn(gm, 'CountNumberCards', [('Hand', K.CARD_C, True)], [('Count', 'int')])
K.ensure_fn(gm, 'DrawPlayerCard')
K.ensure_fn(gm, 'DrawOpponentCard')
K.ensure_fn(gm, 'DrawToFive')
K.ensure_fn(gm, 'CountHigherInDeck', [('Value', 'int')], [('Count', 'int')])
K.ensure_fn(gm, 'OpponentUnseenAverage', [], [('Average', 'float')])
K.ensure_fn(gm, 'PrepareOpponentHand')
K.ensure_fn(gm, 'LoseLives', [('IsPlayer', 'bool'), ('Amount', 'int')])
K.ensure_fn(gm, 'ShowPrompt', [('Msg', 'string')])
K.ensure_fn(gm, 'ShowSummary', [('Msg', 'string')])
K.ensure_fn(gm, 'CannonNotch')
K.compile_bp(gm)

CARD_CLASS = '"/Game/Blueprints/v2/Blueprints/Card_BP.Card_BP_C"'

CODE = {
'FinalValue': """(fn FinalValue (Card)
  (bind mv (Class|CardBP|GetModifiedValue Card))
  (return (select (== mv 0) (Class|CardBP|GetCardValue Card) mv)))""",

'RefillDeck': """(fn RefillDeck ()
  (for v (range 1 11)
    (for _ (range 4)
      (Utilities|Array|Add (Variables|Default|GetInitialDeck) v)))
  (return))""",

'CountNumberCards': """(fn CountNumberCards (Hand)
  (Variables|Default|SetTempCount 0)
  (for c Hand
    (if (not (Class|CardBP|GetIsPowerUp c))
      (Variables|Default|SetTempCount (+ (Variables|Default|GetTempCount) 1))))
  (return (Variables|Default|GetTempCount)))""",

'DrawPlayerCard': """(fn DrawPlayerCard ()
  (if (== (Utilities|Array|Length (Variables|Default|GetInitialDeck)) 0)
    (CallFunction|RefillDeck))
  (bind player (Variables|Default|GetPlayerREF))
  (bind slot (Class|PlayerBP|GetCardSlot1 player))
  (bind card (Game|SpawnActorfromClass :Class %s :SpawnTransform (Transformation|GetWorldTransform slot) :CollisionHandlingOverride "AlwaysSpawn" :Owner self))
  (Utilities|Array|Add (Variables|Default|GetPlayerHand) card)
  (bind deck (Variables|Default|GetInitialDeck))
  (Variables|Default|SetTempA (Math|Random|RandomIntegerinRange 0 (- (Utilities|Array|Length deck) 1)))
  (bind idx (Variables|Default|GetTempA))
  (Class|CardBP|SetCardValue (Utilities|Array|Get(acopy) deck idx) card)
  (Utilities|Array|RemoveIndex deck idx)
  (Class|CardBP|SetOwningPlayer player card)
  (Class|CardBP|SetIsHeld false card)
  (Class|CardBP|RefreshCardText card)
  (Transformation|AttachActorToComponent card slot "None" "SnapToTarget" "SnapToTarget" "SnapToTarget")
  (return))""" % CARD_CLASS,

'DrawOpponentCard': """(fn DrawOpponentCard ()
  (if (== (Utilities|Array|Length (Variables|Default|GetInitialDeck)) 0)
    (CallFunction|RefillDeck))
  (bind opp (Variables|Default|GetOpponentREF))
  (bind slot (Class|OpponentBP|GetCardSlot1 opp))
  (bind card (Game|SpawnActorfromClass :Class %s :SpawnTransform (Transformation|GetWorldTransform slot) :CollisionHandlingOverride "AlwaysSpawn" :Owner self))
  (Utilities|Array|Add (Variables|Default|GetOpponentHand) card)
  (Class|CardBP|SetIsOpponentCard true card)
  (bind deck (Variables|Default|GetInitialDeck))
  (Variables|Default|SetTempA (Math|Random|RandomIntegerinRange 0 (- (Utilities|Array|Length deck) 1)))
  (bind idx (Variables|Default|GetTempA))
  (Class|CardBP|SetCardValue (Utilities|Array|Get(acopy) deck idx) card)
  (Utilities|Array|RemoveIndex deck idx)
  (Class|CardBP|SetOwningOpponent opp card)
  (Class|CardBP|SetIsHeld false card)
  (Class|CardBP|RefreshCardText card)
  (Transformation|AttachActorToComponent card slot "None" "SnapToTarget" "SnapToTarget" "SnapToTarget")
  (return))""" % CARD_CLASS,

'DrawToFive': """(fn DrawToFive ()
  (for _ (range (- 5 (CallFunction|CountNumberCards :Hand (Variables|Default|GetPlayerHand))))
    (CallFunction|DrawPlayerCard))
  (for _ (range (- 5 (CallFunction|CountNumberCards :Hand (Variables|Default|GetOpponentHand))))
    (CallFunction|DrawOpponentCard))
  (CallFunction|RefreshCardLocations)
  (Class|OpponentBP|RefreshOpponentHand (Variables|Default|GetOpponentREF) (Variables|Default|GetOpponentHand))
  (return))""",

'CountHigherInDeck': """(fn CountHigherInDeck (Value)
  (Variables|Default|SetTempCount 0)
  (for v (Variables|Default|GetInitialDeck)
    (if (> v Value)
      (Variables|Default|SetTempCount (+ (Variables|Default|GetTempCount) 1))))
  (return (Variables|Default|GetTempCount)))""",

'OpponentUnseenAverage': """(fn OpponentUnseenAverage ()
  (Variables|Default|SetTempCount 0)
  (Variables|Default|SetTempFloat 0.0)
  (for v (Variables|Default|GetInitialDeck)
    (Variables|Default|SetTempFloat (+ (Variables|Default|GetTempFloat) v))
    (Variables|Default|SetTempCount (+ (Variables|Default|GetTempCount) 1)))
  (for c (Variables|Default|GetPlayerHand)
    (if (not (Class|CardBP|GetIsPowerUp c))
      (Variables|Default|SetTempFloat (+ (Variables|Default|GetTempFloat) (Class|CardBP|GetCardValue c)))
      (Variables|Default|SetTempCount (+ (Variables|Default|GetTempCount) 1))))
  (bind cnt (Variables|Default|GetTempCount))
  (return (select (> cnt 0) (/ (Variables|Default|GetTempFloat) cnt) 5.5)))""",

'PrepareOpponentHand': """(fn PrepareOpponentHand ()
  (bind hand (Variables|Default|GetOpponentHand))
  (bind temp (Variables|Default|GetTempCards))
  (Utilities|Array|Clear temp)
  (for c hand
    (if (not (Class|CardBP|GetIsPowerUp c))
      (Utilities|Array|Add temp c)))
  (if (> (Utilities|Array|Length temp) 0)
    (Variables|Default|SetPickedCard (Utilities|Array|Get(acopy) temp (Math|Random|RandomIntegerinRange 0 (- (Utilities|Array|Length temp) 1))))
    (bind pick (Variables|Default|GetPickedCard))
    (Utilities|Array|RemoveItem hand pick)
    (Utilities|Array|Insert hand pick 0))
  (Class|OpponentBP|RefreshOpponentHand (Variables|Default|GetOpponentREF) hand)
  (return))""",

'LoseLives': """(fn LoseLives (IsPlayer Amount)
  (bind lives (select IsPlayer (Variables|Default|GetPlayerLives) (Variables|Default|GetOpponentLives)))
  (Variables|Default|SetTempA (Math|Integer|Min(Integer) Amount lives))
  (Variables|Default|SetTempB (- lives (Variables|Default|GetTempA)))
  (bind n (Variables|Default|GetTempA))
  (bind left (Variables|Default|GetTempB))
  (if IsPlayer
    (Variables|Default|SetPlayerLives left)
    (for _ (range n)
      (bind pc (Variables|Default|GetPlayerLifeCandles))
      (if (> (Utilities|Array|Length pc) 0)
        (bind candle (Utilities|Array|Get(acopy) pc 0))
        (Class|LifeCandleBP|BlowOutCandle candle)
        (Utilities|Array|RemoveIndex pc 0)))
    (else
      (Variables|Default|SetOpponentLives left)
      (for _ (range n)
        (bind oc (Variables|Default|GetOpponentLifeCandles))
        (if (> (Utilities|Array|Length oc) 0)
          (bind candle (Utilities|Array|Get(acopy) oc 0))
          (Class|LifeCandleBP|BlowOutCandle candle)
          (Utilities|Array|RemoveIndex oc 0)))))
  (Class|CannonBP|LookAt (Variables|Default|GetCannonREF) IsPlayer (== left 0) (not IsPlayer))
  (return))""",

'ShowPrompt': """(fn ShowPrompt (Msg)
  (Class|GeneralWBP|SetPrompt (Variables|Default|GetGeneralWBPREF) Msg)
  (return))""",

'ShowSummary': """(fn ShowSummary (Msg)
  (Class|GeneralWBP|SetSummary (Variables|Default|GetGeneralWBPREF) Msg)
  (return))""",

'CannonNotch': """(fn CannonNotch ()
  (Transformation|AddLocalRotation (Class|CannonBP|GetGun (Variables|Default|GetCannonREF)) :DeltaRotation (Math|Rotator|MakeRotator 0.0 -4.0 0.0))
  (Audio|PlaySound2D "/Game/Audio/SE/GunAdjust.GunAdjust" 0.6)
  (return))""",
}

only = globals().get('ONLY')
for name, code in CODE.items():
    if only and name not in only:
        continue
    try:
        K.write(gm, name, code)
        print('OK', name)
    except Exception as e:
        print('ERR', name, str(e)[:700])
try:
    K.compile_bp(gm)
    print('COMPILED')
except Exception as e:
    print('COMPILE ERR', str(e)[:3000])
