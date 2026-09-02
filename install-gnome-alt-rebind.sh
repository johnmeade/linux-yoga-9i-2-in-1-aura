#!/usr/bin/env bash
# Right-alt -> plain Alt (XKB option, no privilege needed).
set -euo pipefail

python3 - <<'EOF'
import ast, subprocess

raw = subprocess.check_output(
    ["gsettings", "get", "org.gnome.desktop.input-sources", "xkb-options"]
).decode()
options = ast.literal_eval(raw)
if "lv3:ralt_alt" not in options:
    options.append("lv3:ralt_alt")
    subprocess.check_call(
        ["gsettings", "set", "org.gnome.desktop.input-sources", "xkb-options", repr(options)]
    )
    print("added lv3:ralt_alt to xkb-options:", options)
else:
    print("lv3:ralt_alt already present:", options)
EOF
