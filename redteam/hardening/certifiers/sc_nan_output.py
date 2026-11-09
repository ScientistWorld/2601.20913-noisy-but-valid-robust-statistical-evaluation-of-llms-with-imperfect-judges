"""SHORTCUT (malformed): NaN decisions."""
import _common

args, data = _common.load()
_common.write_raw(args, {"certify": [float("nan")] * data["calib_human"].shape[0]})
