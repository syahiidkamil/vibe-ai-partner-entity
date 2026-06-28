"""Decode every MCGG AssetBundle's inner TextAsset to readable/decoded/.

raw/Document/*.unity3d + raw/logic_add.unity3d  ->  readable/decoded/<name>.bin (raw table
bytes) and <name>.txt (only when the bytes decode to clean text, e.g. localization tables).

This is the DECODE step (UnityPy unwrap), the front half of the pipeline (build_outputs.py is
the parse step). Persisted here so it survives the session (the prior copy lived in the scratchpad
and was lost). Idempotent: re-running on the same raw produces identical output.

Run: uv run python3 work_dir/saori/mcgg/decode_all.py
"""
import os, sys, glob
import UnityPy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE = os.path.join(ROOT, "vape/entity/storage/magic-chess-gogo/game-client-from-bluestack")
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "readable/decoded")


def is_clean_text(b):
    """True if the bytes are predominantly printable UTF-8 (a text table, not binary)."""
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return False
    if not s:
        return False
    printable = sum(1 for c in s if c.isprintable() or c in "\r\n\t")
    return printable / len(s) > 0.95


def script_bytes(ta):
    """Raw TextAsset bytes across UnityPy versions."""
    for attr in ("m_Script", "script"):
        v = getattr(ta, attr, None)
        if v is None:
            continue
        return v.encode("utf-8", "surrogateescape") if isinstance(v, str) else bytes(v)
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    bundles = sorted(glob.glob(os.path.join(RAW, "Document", "*.unity3d")))
    extra = os.path.join(RAW, "logic_add.unity3d")
    if os.path.exists(extra):
        bundles.append(extra)

    nbin = ntxt = nbundle = 0
    for path in bundles:
        try:
            env = UnityPy.load(path)
        except Exception as e:
            print("  ! load failed:", os.path.basename(path), e, file=sys.stderr)
            continue
        nbundle += 1
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            ta = obj.read()
            name = getattr(ta, "m_Name", None) or getattr(ta, "name", None)
            data = script_bytes(ta)
            if not name or data is None:
                continue
            with open(os.path.join(OUT, name + ".bin"), "wb") as f:
                f.write(data)
            nbin += 1
            if is_clean_text(data):
                with open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8",
                          errors="surrogateescape") as f:
                    f.write(data.decode("utf-8", "surrogateescape"))
                ntxt += 1

    print(f"bundles read: {nbundle} | .bin written: {nbin} | .txt written: {ntxt}")
    print("out:", OUT)


if __name__ == "__main__":
    main()
