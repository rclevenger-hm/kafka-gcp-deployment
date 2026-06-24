#!/usr/bin/env python3
"""Validate Python syntax, local documentation links and tracked asset references."""
import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def main():
    errors=[]
    for folder in ("bootstrap", "tools", "tests"):
        for file in (ROOT/folder).glob("*.py"):
            try: ast.parse(file.read_text(),filename=str(file))
            except SyntaxError as error: errors.append(str(error))
    docs=[ROOT/"README.md",*list((ROOT/"docs").rglob("*.md")),ROOT/"terraform/README.md"]
    for file in docs:
        if not file.exists():
            errors.append("Missing document: "+str(file.relative_to(ROOT))); continue
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)",file.read_text()):
            if re.match(r"[a-z]+:",target) or target.startswith("#"): continue
            path=target.split("#",1)[0]
            if not (file.parent/path).exists(): errors.append(f"Broken link: {file.relative_to(ROOT)} -> {target}")
    json.loads((ROOT/"monitoring/grafana-dashboard.json").read_text())
    for file in (ROOT/"bootstrap").iterdir():
        if file.is_file() and "REPLACE_JMX_DIGEST" in file.read_text(): errors.append("Unpinned exporter digest")
    if errors: raise SystemExit("\n".join(errors))
    print("Repository syntax, local links and dashboard JSON passed")

if __name__ == "__main__": main()
