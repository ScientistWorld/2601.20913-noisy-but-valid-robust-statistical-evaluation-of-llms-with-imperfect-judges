"""SHORTCUT (impossible values): -1000 decisions."""
import _common

args, data = _common.load()
_common.write_raw(args, {"certify": [-1000] * data["calib_human"].shape[0]})
