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


def number_to_pattern(num: float):
    """
    Converts number to a pattern. First converts the number to IEEE 754
    floating point, then constructs a pattern representing that floating
    point number.
    """
    if num == 0:
        return "aqaa"

    pattern = []

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
    pattern.append(("d" if exponent < 0 else "a") * abs(exponent))

    # Optimizing pass, to remove mul-2 and div-2 operations that cancel
    # out.
    out = []
    for subseq in "".join(pattern).split("w"):
        acc = sum(-1 if op == "d" else 1 for op in subseq)
        out.append(("d" if acc < 0 else "a") * abs(acc))

    return ("aqaa" if num > 0 else "dedd") + "w".join(out)


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
