from HexMod.doc.collate_data import fetch_patterns

# Parse and collect list of all "vanilla" spells.
# Frankenstein code :)
# TODO: Do not directly expose all builtins. Most patterns should not be
# directly invocable, such as stack manipulation.
builtin_patterns = {
    k[1:]: v[0]
    for k, v in fetch_patterns(
        {"resource_dir": "HexMod/Common/src/main/resources", "modid": ""}
    ).items()
    if "interop" not in k
}

# Handy aliases
builtin_patterns |= {
    "+": builtin_patterns["add"],
    "-": builtin_patterns["sub"],
    "*": builtin_patterns["mul_dot"],
    "/": builtin_patterns["div_cross"],
    "%": builtin_patterns["modulo"],
    "^": builtin_patterns["pow_proj"],
    "ONE": ("aqaaw"),
    "NEGATIVE_ONE": ("deddw"),
}
