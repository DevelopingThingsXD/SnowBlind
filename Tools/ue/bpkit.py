"""Helpers that run INSIDE the Unreal Editor (send via Tools/ue/uepy.py) for scripted Blueprint edits.

Usage from a script sent with uepy.py:
    import sys; sys.path.insert(0, "B:/SnowBlind/Tools/ue")
    import importlib, bpkit; importlib.reload(bpkit)
    gm = bpkit.L(bpkit.GM)
"""
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, ContainerType

V2 = "/Game/Blueprints/v2/Blueprints/"
GM = V2 + "CardWar_GM.CardWar_GM"
CARD_C = V2 + "Card_BP.Card_BP_C"
OPP = V2 + "Opponent_BP.Opponent_BP"
PLAYER = V2 + "Player_BP.Player_BP"
CANNON = V2 + "Cannon_BP.Cannon_BP"
WBP = "/Game/Blueprints/v2/UI/General_WBP.General_WBP"


def L(path):
    a = unreal.load_asset(path)
    if a is None:
        raise RuntimeError(f"cannot load {path}")
    return a


def C(path):
    c = unreal.load_class(None, path) if path.startswith("/Script/") else unreal.load_object(None, path)
    if c is None:
        raise RuntimeError(f"cannot load class {path}")
    return c


def ensure_var(bp, name, type_name, arr=False):
    """type_name: basic type ('int','bool','string',...) or a class path ('/Game/...X_C', '/Script/Engine.Actor')."""
    if name in BT.list_variables(bp):
        return False
    ct = ContainerType.ARRAY if arr else None
    if type_name.startswith("/"):
        BT.add_object_variable(bp, name, C(type_name), None, ct)
    else:
        BT.add_variable(bp, name, type_name, None, ct)
    return True


def _param(g, name, type_name, is_input, arr=False):
    ct = ContainerType.ARRAY if arr else None
    if type_name.startswith("/"):
        BT.add_object_function_param(g, name, C(type_name), is_input, ct)
    else:
        BT.add_function_param(g, name, type_name, is_input, ct)


def ensure_fn(bp, name, ins=(), outs=()):
    """Create function graph with params if missing. ins/outs: [(name, type)] or [(name, type, True)] for arrays."""
    existing = [g.get_name() for g in BT.list_graphs(bp)]
    g = BT.add_function_graph(bp, name)
    if name not in existing:
        for p in ins:
            _param(g, p[0], p[1], True, len(p) > 2 and p[2])
        for p in outs:
            _param(g, p[0], p[1], False, len(p) > 2 and p[2])
    return g


def write(bp, graph_name, code, compile=True):
    """Like BlueprintTools.write_graph_dsl, but raises transpile errors instead of swallowing them."""
    from editor_toolset.toolsets import blueprint_dsl as D
    g = BT.get_graph(bp, graph_name)
    D.Transpiler(g, BT.create_node, BT.connect_pins, BT._get_node_info, BT.set_pin_value,
                 lambda gg: BT.find_nodes(gg), delete_node_fn=BT.delete_node,
                 find_node_types_fn=lambda f: BT.find_node_types(g, f)).transpile(code)
    if compile:
        BT.compile_blueprint(bp)


def prune(bp, graph_name, dry_run=False):
    """Delete nodes not reachable from an entry/event node (via exec flow, plus pure nodes feeding them).
    Comment nodes are kept. Returns list of deleted node names."""
    g = BT.get_graph(bp, graph_name)
    infos = BT.get_node_infos(BT.find_nodes(g))
    by_name = {str(i.node.get_name()): i for i in infos}
    entries = {str(i.node.get_name()) for i in BT.get_node_infos(BT.find_nodes(g, entry_points_only=True))}
    live = set(entries)
    stack = list(entries)
    while stack:  # exec flow forward
        n = by_name.get(stack.pop())
        if not n:
            continue
        for p in n.output_pins:
            if p.type_id == 'Exec':
                for c in p.connected_pins:
                    cn = str(c.node.get_name())
                    if cn not in live:
                        live.add(cn); stack.append(cn)
    stack = list(live)
    while stack:  # data dependencies backward
        n = by_name.get(stack.pop())
        if not n:
            continue
        for p in n.input_pins:
            if p.type_id != 'Exec':
                for c in p.connected_pins:
                    cn = str(c.node.get_name())
                    if cn not in live:
                        live.add(cn); stack.append(cn)
    dead = [i for name, i in by_name.items() if name not in live and 'Comment' not in i.type_id]
    if not dry_run:
        for i in dead:
            BT.delete_node(i.node)
    return [str(i.node.get_name()) for i in dead]


def read(bp, graph_name):
    return BT.read_graph_dsl(BT.get_graph(bp, graph_name))


def compile_bp(bp):
    BT.compile_blueprint(bp)


def save(*bps):
    for bp in bps:
        unreal.EditorAssetLibrary.save_loaded_asset(bp, False)


def set_defaults(bp, values: dict):
    """Set CDO defaults (compile first)."""
    cdo = unreal.get_default_object(bp.generated_class())
    for k, v in values.items():
        cdo.set_editor_property(k, v)
