# hexpiler (WIP)
> A proof-of-concept Domain-Specific Language for hex casting.

hexpiler is a transpiler for hexlisp targeting Hex Casting patterns.

hexlisp is a Domain-Specific Language for the Minecraft [Hex Casting](https://github.com/gamma-delta/HexMod) mod. Its grammar can be found in [hexlisp.grammar](hexlisp.grammar).

Please file an issue if something is broken!

## Requirements

* Python 3.10+
* Packages in `requirements.txt`

## Todo

* [x] Expressions
  * [X] Lists
  * [x] Vector3s
  * [x] Floats
  * [x] Pattern casting
  * [ ] Escaped patterns
* [ ] Conditionals
* [ ] Loops
* [ ] Builtin functions *(currently all patterns can be invoked as functions, but this is probably not safe or intended)*
* [ ] Variable binding
* [ ] Function binding

## Usage

```
usage: hexpiler [-h] [-d] file

A hexlisp transpiler for the Hex Casting mod. Heavy WIP.

positional arguments:
  file         Input file.

options:
  -h, --help   show this help message and exit
  -d, --debug  Print debug info.
```

## Language Reference

TODO

## License
[MIT](https://choosealicense.com/licenses/mit/)
