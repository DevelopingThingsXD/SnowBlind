# M1: hook the new round flow into the jam's play path (run inside editor via Tools/ue/uepy.py)
import sys; sys.path.insert(0, 'B:/SnowBlind/Tools/ue')
import importlib, bpkit as K; importlib.reload(K)
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as BT

gm = K.L(K.GM)

OPPONENT_PLAY_CARD = """(fn OpponentPlayCard (playedCard ChosenPowerUpCard)
  (bind opp (Variables|Default|GetOpponentREF))
  (bind held (Class|OpponentBP|GetHeldCard opp))
  (Class|CardBP|SetCardState held "NewEnumerator3")
  (Transformation|DetachFromActor held "KeepWorld" "KeepWorld" "KeepWorld")
  (Class|CardBP|SetTargetRelativeLocation (Math|Transform|InverseTransformLocation (Transformation|GetWorldTransform (Class|OpponentBP|GetCardSlot1 opp)) (Transformation|GetWorldLocation (Class|PlayAreaPlayerBP|GetOpponentCardSlot (Variables|Default|GetPlayAreaREF)))) held)
  (Class|CardBP|SetTargetRelativeRotation "-90.000000,180.000000,0.000000" held)
  (Variables|Default|SetOpponentCommittedCard held)
  (Class|OpponentBP|SetHeldCard :self opp)
  (Variables|Default|SetPendingPlayerCard (Variables|Default|GetPlayerCommittedCard))
  (Variables|Default|SetPendingOpponentCard (Variables|Default|GetOpponentCommittedCard))
  (Variables|Default|SetPendingOppPowerUp ChosenPowerUpCard)
  (CallFunction|BeginWager)
  (return))"""

CARD_PLAY_SEQUENCE = """(event Custom|CardPlay_Sequence
  (CallFunction|PrepareOpponentHand)
  (bind (pcard pup) (Class|OpponentBP|PlayCard (Variables|Default|GetOpponentREF)))
  (Utilities|FlowControl|Delay 1.0)
  (CallFunction|OpponentPlayCard :playedCard pcard :ChosenPowerUpCard pup))"""

step = globals().get('STEP', 'all')
if step in ('all', 'opc'):
    K.write(gm, 'OpponentPlayCard', OPPONENT_PLAY_CARD, compile=False); print('OK OpponentPlayCard')
if step in ('all', 'seq'):
    K.write(gm, 'EventGraph', CARD_PLAY_SEQUENCE, compile=False); print('OK CardPlay_Sequence')

if step in ('all', 'begin'):
    # Surgical: BeginPlay ... -> SpawnOpponentHand -> StartRound
    g = BT.get_graph(gm, 'EventGraph')
    infos = BT.get_node_infos(BT.find_nodes(g))
    spawn = [n for n in infos if n.type_id.endswith('SpawnOpponentHand')]
    already = [n for n in infos if n.type_id == 'CallFunction|StartRound']
    if spawn and not already:
        sp = spawn[0]
        then_pin = [p for p in sp.output_pins if p.type_id == 'Exec'][0]
        if not then_pin.connected_pins:
            node = BT.create_node(g, 'CallFunction|StartRound', unreal.IntPoint(sp.position.x + 400, sp.position.y))
            ni = BT.get_node_infos([node])[0]
            exec_in = [p for p in ni.input_pins if p.type_id == 'Exec'][0]
            BT.connect_pins(then_pin.pin_id, exec_in.pin_id)
            print('OK BeginPlay -> StartRound')
        else:
            print('SpawnOpponentHand exec already connected to', [str(c.node.get_name()) for c in then_pin.connected_pins])
    else:
        print('skip begin', len(spawn), len(already))

try:
    K.compile_bp(gm); K.save(gm); print('COMPILED+SAVED')
except Exception as e:
    print('COMPILE ERR', str(e)[:4000])
