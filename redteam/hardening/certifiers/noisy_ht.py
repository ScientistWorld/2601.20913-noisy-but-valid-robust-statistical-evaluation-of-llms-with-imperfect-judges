"""REFERENCE: runs the shipped method/certifiers/noisy_ht.py unchanged."""
import runpy

import _common

runpy.run_path(str(_common.ROOT / "method" / "certifiers" / "noisy_ht.py"), run_name="__main__")
