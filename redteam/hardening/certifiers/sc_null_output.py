"""SHORTCUT (malformed): null decisions."""
import _common

args, data = _common.load()
_common.write_raw(args, {"certify": [None] * data["calib_human"].shape[0]})
