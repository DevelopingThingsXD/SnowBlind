# Run Python inside the running Unreal Editor via the engine's remote_execution module.
# Usage: python uepy.py <file.py | -c "code">
import sys, time, json
sys.path.insert(0, r"B:/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python")
import remote_execution as re_
cfg = re_.RemoteExecutionConfig(); cfg.multicast_bind_address = "127.0.0.1"
rex = re_.RemoteExecution(cfg); rex.start()
try:
    for _ in range(30):
        if rex.remote_nodes: break
        time.sleep(0.2)
    if not rex.remote_nodes: print("NO_EDITOR_NODE"); sys.exit(2)
    rex.open_command_connection(rex.remote_nodes[0]["node_id"])
    code = sys.argv[2] if sys.argv[1] == "-c" else open(sys.argv[1], encoding="utf-8").read()
    res = rex.run_command(code, unattended=True, exec_mode=re_.MODE_EXEC_FILE)
    for o in res.get("output", []): print(o.get("output", "").rstrip())
    if not res.get("success"): print("FAILED:", res.get("result")); sys.exit(1)
finally:
    rex.stop()
