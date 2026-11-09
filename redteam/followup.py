"""Resolve comparison-row validation failures without using hidden data."""
import json
import subprocess
from pathlib import Path

ROOT=Path('/home/user')

for name in ['visible_seed_43_reference','baseline_fields_shortcut','oracle_comparator_shortcut']:
    # Preserve the initial failed attempt, including its actual produced scores.
    folder=ROOT/'redteam'/name
    folder.mkdir(exist_ok=True)
    for filename in ['scores.json','result.json']:
        src=folder/filename
        if src.exists():
            dest=folder/('initial_'+filename)
            if not dest.exists(): dest.write_bytes(src.read_bytes())
    subprocess.run(['bash',f'redteam/{name}/run.sh'],cwd=ROOT,check=True)
    result=json.loads((folder/'result.json').read_text())
    print(name,result.get('test_returncode'),flush=True)
subprocess.run(['/usr/bin/python3','redteam/summarize.py'],cwd=ROOT,check=True)
