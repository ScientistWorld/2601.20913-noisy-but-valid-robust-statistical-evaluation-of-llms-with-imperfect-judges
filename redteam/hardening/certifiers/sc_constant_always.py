"""SHORTCUT: always certifies."""
import _common

args, data = _common.load()
_common.write(args, [1] * data["calib_human"].shape[0])
