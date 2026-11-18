"""
Blueprint index: dumps a readable outline of every Blueprint in Content/ WITHOUT opening Unreal.

How it works: every saved Blueprint .uasset carries "FiBData" (Find-in-Blueprints search data)
in its asset-registry header: a lookup table of FText strings + a JSON tree of graphs, nodes,
pins (with default values), variables (with defaults), and components. We decode that.

What you get: variables + defaults, components, every graph/function/macro with its nodes and
any non-trivial pin literals. What you DON'T get: wires between nodes (execution order is
implied, not exact). For exact flow, read the graph in-editor or via the Unreal MCP EditorToolset.

Usage (from repo root):   python Tools/bp_index.py            -> writes Saved/BlueprintIndex/*.txt
                          python Tools/bp_index.py Content/Blueprints/v2   (limit to a folder)
"""
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "Saved" / "BlueprintIndex"


def decode_fib(path):
    d = path.read_bytes()
    i = d.find(b"FiBData\x00")
    if i < 0:
        return None
    n = -struct.unpack("<i", d[i + 8:i + 12])[0]
    if n <= 0:
        return None
    u = struct.unpack("<%dH" % n, d[i + 12:i + 12 + 2 * n])
    b = bytes(max(0, min(x - 1, 255)) for x in u)  # table section: each byte stored as (byte+1)
    pos = 0

    def i32():
        nonlocal pos
        v = struct.unpack_from("<i", b, pos)[0]
        pos += 4
        return v

    def i8():
        nonlocal pos
        v = struct.unpack_from("<b", b, pos)[0]
        pos += 1
        return v

    def fstr():
        nonlocal pos
        ln = i32()
        if ln == 0:
            return ""
        if ln < 0:
            v = b[pos:pos - 2 * ln].decode("utf-16-le", "replace").rstrip("\x00")
            pos += -2 * ln
            return v
        v = b[pos:pos + ln - 1].decode("latin1")
        pos += ln
        return v

    def ftext():
        nonlocal pos
        i32()  # flags
        ht = i8()
        if ht == 0:  # Base: namespace, key, source
            fstr(); fstr()
            return fstr()
        if ht == -1:  # None
            return fstr() if i32() else ""
        if ht in (1, 2, 3):  # Named/Ordered/Argument format
            fmt = ftext()
            for _ in range(i32()):
                if ht in (1, 3):
                    fstr()
                t = i8()
                if t in (0, 1, 3):
                    pos += 8
                elif t == 2:
                    pos += 4
                elif t == 4:
                    ftext()
                elif t == 5:
                    pos += 1
            return fmt
        raise ValueError(f"unsupported FText history {ht}")

    i32(); i32()  # version, size
    table = {}
    for _ in range(i32()):
        k = i32()
        table[k] = ftext()
    body = "".join(chr(x) for x in u[pos:])
    body = body[body.find("{"):body.rfind("}") + 1]
    try:
        j = json.loads(body)
    except json.JSONDecodeError:
        j = json.loads("".join(chr(ord(c) + 1) for c in body))

    def res(x):
        if isinstance(x, dict):
            return {res(k): res(v) for k, v in x.items()}
        if isinstance(x, list):
            return [res(v) for v in x]
        if isinstance(x, str) and x.isdigit() and int(x) in table:
            return table[int(x)]
        return x

    return res(j)


TRIVIAL = {"", "0", "0.0", "0.000000", "false", "None", "0, 0, 0", "self", "()",
           "0.000000,0.000000,0.000000", '(Linkage=-1,UUID=-1,ExecutionFunction="",CallbackTarget=None)'}
NOISE_PREFIX = ("Target=/Script/",)


def outline(j):
    L = []
    for pr in j.get("Properties", []):
        dv = pr.get("DefaultValue", "")
        line = f'VAR {pr["Name"]}: {pr.get("PinCategory")}{"[]" if pr.get("IsArray") else ""}'
        if dv not in ("", [], None, {}, "None"):
            line += f" = {json.dumps(dv)}"
        if pr.get("Tooltip"):
            line += f'  // {pr["Tooltip"]}'
        L.append(line)
    for c in j.get("Components", []):
        L.append(f'COMP {c["Name"]} : {c.get("ObjectClass", "").split(".")[-1]}')
    for sec in ("Uber", "Functions", "Macros"):
        for g in j.get(sec, []):
            L.append(f'\n=== {sec}: {g.get("Name")}')
            for pr in g.get("Properties", []):
                L.append(f'  local {pr["Name"]}: {pr.get("PinCategory")}')
            for n in g.get("Nodes", []):
                if n.get("ClassName") == "K2Node_Knot":
                    continue
                pins = []
                for p in n.get("Pins", []):
                    dv = str(p.get("DefaultValue", ""))
                    if p.get("PinCategory") == "exec" or dv in TRIVIAL or dv.startswith("(R="):
                        continue
                    s = f'{p.get("Name") or "?"}={dv}'
                    if not s.startswith(NOISE_PREFIX) and not s.startswith("Target=/Script/"):
                        pins.append(s)
                s = "  " + n.get("Name", "?")
                if pins:
                    s += " [" + ", ".join(pins) + "]"
                if n.get("Comment"):
                    s += "  // " + n["Comment"].replace("\n", " ")
                L.append(s)
    return "\n".join(L)


def main():
    base = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "Content")
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for p in sorted(base.rglob("*.uasset")):
        if "__External" in p.parts:
            continue
        try:
            j = decode_fib(p)
        except Exception as e:  # keep going; report
            print(f"skip {p.relative_to(ROOT)}: {e}")
            continue
        if not j:
            continue
        name = str(p.relative_to(ROOT / "Content").with_suffix("")).replace("\\", "/").replace("/", "__")
        (OUT / f"{name}.txt").write_text(outline(j), encoding="utf-8")
        count += 1
    print(f"wrote {count} outlines to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
