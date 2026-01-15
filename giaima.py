import ast
import base64
import marshal
import zlib
import bz2
import lzma
import sys
import re
from textwrap import indent

MAX_DEPTH = 10

def try_decode(data: bytes):
    results = []

    for name, func in [
        ("base64", base64.b64decode),
        ("base85", base64.b85decode),
        ("zlib", zlib.decompress),
        ("bz2", bz2.decompress),
        ("lzma", lzma.decompress),
    ]:
        try:
            out = func(data)
            results.append((name, out))
        except Exception:
            pass

    try:
        out = marshal.loads(data)
        results.append(("marshal", out))
    except Exception:
        pass

    return results


def extract_strings(code):
    return re.findall(rb"(?:b)?['\"]([A-Za-z0-9+/=]{40,})['\"]", code)


def deobfuscate_bytes(data, depth=0):
    if depth > MAX_DEPTH:
        return data

    decoded = try_decode(data)
    for name, out in decoded:
        print(f"[+] Decoded via {name} at depth {depth}")
        if isinstance(out, bytes):
            return deobfuscate_bytes(out, depth + 1)
        elif isinstance(out, str):
            return out.encode()
        else:
            return repr(out).encode()

    return data


def strip_exec_eval(code: str):
    tree = ast.parse(code)
    cleaned = []

    for node in tree.body:
        if isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                if getattr(node.value.func, "id", "") in ("exec", "eval"):
                    cleaned.append(ast.get_source_segment(code, node))
                    continue
        cleaned.append(ast.get_source_segment(code, node))

    return "\n".join([c for c in cleaned if c])


def main():
    if len(sys.argv) != 2:
        print("Usage: python deobfuscate_python.py <file.py>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        raw = f.read()

    print("[*] Extracting encoded strings...")
    strings = extract_strings(raw)

    output = raw
    for s in strings:
        try:
            decoded = deobfuscate_bytes(s)
            if decoded != s:
                output = output.replace(s, decoded)
        except Exception:
            pass

    try:
        code = output.decode(errors="ignore")
        code = strip_exec_eval(code)
    except Exception:
        code = output.decode(errors="ignore")

    with open("deobfuscated_output.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("[✓] Done. Output saved as deobfuscated_output.py")


if __name__ == "__main__":
    main()
