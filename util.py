import struct

import nbtlib
import numpy
from bitarray import bitarray
from bitarray.util import ba2int
from nbtlib import schema

START_ANGLE = 0
ANGLES = {"w": 0, "e": 1, "d": 2, "s": 3, "a": 4, "q": 5}

FocusSchema = schema(
    "FocusSchema",
    {
        "data": schema(
            "Data",
            {
                "list": nbtlib.List[
                    schema(
                        "ListEntry",
                        {
                            "pattern": schema(
                                "Pattern",
                                {"angles": nbtlib.ByteArray, "start_dir": nbtlib.Byte},
                            )
                        },
                    )
                ]
            },
        )
    },
)


# TODO: Add optimising pass to remove consecutive mul-2 and div-2 ops.
def number_to_pattern(num: float):
    """
    Converts number to a pattern. First converts the number to IEEE 754
    floating point, then constructs a pattern representing that floating
    point number.
    """
    pattern = []
    if num < 0:
        # Negated number pattern prefix
        pattern.append("dedd")
    elif num > 0:
        pattern.append("aqaa")
    else:
        return "aqaa"

    fp = bitarray()
    fp.frombytes(struct.pack("!d", num))

    exponent = fp[1:12]
    mantissa = fp[12:]

    pattern.append("wa")
    for bit in mantissa[:-1]:
        if bit == 1:
            pattern.append("w")
        pattern.append("a")

    if mantissa[-1] == 1:
        pattern.append("w")

    pattern.append("d" * 52)

    exponent = ba2int(exponent) - 1023
    pattern.append("d" if exponent < 0 else "a" * abs(exponent))

    return "".join(pattern)


def patterns_to_give_command(patterns: list[str]):
    """
    Generates a give command to give a focus containing the pattern
    list.
    """
    base_cmd = "/give @p hexcasting:focus"

    nbt: nbtlib.CompoundSchema = FocusSchema(
        {
            "data": {
                "list": [
                    {
                        "pattern": {
                            "angles": numpy.array([ANGLES[a] for a in pattern]),
                            "start_dir": START_ANGLE,
                        },
                    }
                    for pattern in patterns
                ]
            }
        }
    )

    return base_cmd + nbtlib.serialize_tag(nbt, compact=True)
