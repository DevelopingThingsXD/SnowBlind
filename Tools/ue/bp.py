# Helpers imported inside the editor (via uepy.py) for Blueprint graph work.
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
from editor_toolset.toolsets.blueprint_dsl import *  # noqa
def load(path):
    return unreal.load_asset(path)
def graph(bp, name):
    return BT.get_graph(bp, name)
def dsl(bp, name):
    return BT.read_graph_dsl(BT.get_graph(bp, name))
