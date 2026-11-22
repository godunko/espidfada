#!/usr/bin/env python3
"""Generate static Ada size/alignment constants from one target C probe object."""

import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile


RESERVED = set("""abort abs abstract accept access aliased all and array at begin body case
constant declare delay delta digits do else elsif end entry exception exit for
function generic goto if in interface is limited loop mod new not null of or
others out overriding package parallel pragma private procedure protected raise
range record rem renames requeue return reverse select separate some subtype
synchronized tagged task terminate then type until use when while with xor
""".split())


def identifier(name):
    return (re.fullmatch(r"[A-Za-z](?:[A-Za-z0-9]|_(?=[A-Za-z0-9]))*", name)
            is not None and name.lower() not in RESERVED)


def validate_package(package):
    if not all(identifier(part) for part in package.split(".")):
        raise ValueError(f"Invalid Ada package name: {package!r}")


def decode(symbols):
    constants = {}
    for line in symbols.splitlines():
        fields = line.split()
        if not fields:
            continue
        symbol = fields[-1]
        prefix = next((p for p in ("espidfada_sizeof_", "espidfada_alignof_")
                       if symbol.startswith(p)), None)
        if prefix is None:
            continue
        if (len(fields) != 4 or not fields[0].isdigit()
                or not fields[1].isdigit() or fields[2] not in ("R", "D", "B")):
            raise ValueError(f"Malformed probe symbol: {line}")
        suffix = symbol[len(prefix):]
        if not identifier(suffix):
            raise ValueError(f"Invalid Ada probe name: {suffix!r}")
        name = prefix.removeprefix("espidfada_") + suffix
        key = name.lower()
        if key in constants:
            raise ValueError(f"Duplicate Ada constant: {name}")
        value = int(fields[1], 10) - 1
        # GNU C permits empty structs with sizeof == 0; alignment stays positive.
        if value < 0 or (prefix == "espidfada_alignof_" and value == 0):
            raise ValueError(f"Invalid size/alignment encoding for {symbol}")
        constants[key] = (name, value)
    if not constants:
        raise ValueError("No size/alignment probe symbols found")
    return [constants[key] for key in sorted(constants)]


def generate(package, symbols):
    validate_package(package)
    constants = decode(symbols)
    return (
        "--  Generated from target C headers and sdkconfig. Do not edit.\n"
        "--  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception\n\n"
        f"package {package} with Pure is\n\n"
        + "".join(f"   {name} : constant := {value};\n" for name, value in constants)
        + f"\nend {package};\n"
    )


def write_if_changed(output, content):
    if output.exists() and output.read_text() == content:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=output.parent,
                                         prefix=output.name + ".", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nm", required=True)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        validate_package(args.package)
        symbols = subprocess.check_output(
            [args.nm, "-S", "--radix=d", "--defined-only", str(args.object)],
            text=True)
        write_if_changed(args.output, generate(args.package, symbols))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"generate_constants: {error}\n")


if __name__ == "__main__":
    main()
