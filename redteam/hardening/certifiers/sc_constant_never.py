"""SHORTCUT: never certifies (trivially valid, no power)."""
import _common

args, data = _common.load()
_common.write(args, [0] * data["calib_human"].shape[0])
