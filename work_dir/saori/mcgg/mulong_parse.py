"""
Parser for Moonton's `$mulonggame_table_1` binary game-table format (Magic Chess: GO GO).

Derived byte-exact by aligning our v302.2 .bin files against a friend's v302.1 JSON
(RelationSkill, MCHeroStarlevel, MCEquipBase, AttrbuteDescribe, AllLanguageEN).

FORMAT SPEC
===========
Header (all tables):
    [0:20]   ASCII magic  b"$mulonggame_table_1\\x00"   (20 bytes)
    [20]     version byte (ASCII digit '0'..'6')        (1 byte)
    [21:25]  int32  rowCount  (little-endian)
    [25:29]  int32  colCount  (little-endian)

The .bin carries NO per-column type metadata: rows are a flat value stream whose
schema (ordered columns + types) is external (the game's compiled C# class). We
recover that schema from a reference parse (the friend's per-table JSON) via type
inference (`infer_schema`).

Value encodings (shared by all row versions):
    int32   : 4 bytes LE
    float32 : 4 bytes LE  (e.g. 00 00 80 3f = 1.0)
    string  : .NET 7-bit-encoded-int length prefix, then UTF-8 bytes
    array   : 7-bit-encoded-int element count, then that many elements
              (elements may themselves be arrays -> nested)
    localized name/desc field : consumes ZERO bytes (text lives in a language
              table; in the source class the value is a runtime lookup). Detected
              as a column that is null in every reference row -> kind "skip".

Row layouts by version byte:
    '0' : rows are simply the flat value stream, one column after another.
    '1' : each row begins with an 8-byte (uint64 LE) presence bitmask; bit i (LSB
          = column 0) marks column i present. Absent columns take the default
          (0 / "" / [] / null). Localized "skip" columns consume 0 bytes whether
          their bit is set or not.
    '2' : after colCount there is an extra int32 dictOffset. Rows are packed tight
          like ver-0 BUT the primary key (column 0) is omitted from each row. At
          dictOffset sits a table of rowCount (int32 pkey, int32 absoluteRowOffset)
          pairs; each row's pk is back-filled by matching its byte offset. Rows
          end exactly at dictOffset.
    '3' : (not needed here; the big MLBB Item.bin / EquipBase.bin stubs) left
          unparsed by this module.
    '6' : localization. After colCount: int32 indexOffset, int32 indexEnd. Then a
          packed string pool. At indexOffset: int32 indexByteSize, int32 count,
          then count (uint32 stringId, int32 poolOffset) pairs. Each poolOffset
          points at a 7-bit-length-prefixed string in the pool. -> {stringId:text}.
          (The stringId is a stable per-string id, not a content hash.)
"""
import struct, json

MAGIC = b"$mulonggame_table_1\x00"


# ---------- low-level readers ----------

def _read_7bit(data, off):
    """.NET Read7BitEncodedInt -> (value, new_offset)."""
    val = 0
    shift = 0
    while True:
        b = data[off]; off += 1
        val |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return val, off


def _read_string(data, off):
    n, off = _read_7bit(data, off)
    return data[off:off + n].decode("utf-8", "surrogateescape"), off + n


def _default_for(kind):
    if kind == "i":
        return 0
    if kind == "f":
        return 0.0
    if kind == "s":
        return ""
    if kind == "skip":
        return None
    if kind.startswith("a:"):
        return []
    return None


def _read_value(data, off, kind):
    if kind == "skip":
        return None, off
    if kind == "i":
        return struct.unpack_from("<i", data, off)[0], off + 4
    if kind == "f":
        return struct.unpack_from("<f", data, off)[0], off + 4
    if kind == "s":
        return _read_string(data, off)
    if kind.startswith("a:"):
        elem = kind[2:]
        cnt, off = _read_7bit(data, off)
        arr = []
        for _ in range(cnt):
            v, off = _read_value(data, off, elem)
            arr.append(v)
        return arr, off
    raise ValueError("unknown kind %r" % kind)


# ---------- schema inference from a reference JSON ----------

def _infer_kind_from_value(v):
    """Kind of a single (non-None) value; arrays recurse."""
    if isinstance(v, bool):
        return "i"
    if isinstance(v, float):
        return "f"
    if isinstance(v, int):
        return "i"
    if isinstance(v, str):
        return "s"
    if isinstance(v, list):
        return "a:?"  # element kind filled by column-level pass
    return "?"


def infer_schema(rows):
    """Given a list of dict rows (the friend's parse), return [(name, kind)]
    in column order. Float beats int; any-float in an array -> float array;
    nested arrays handled recursively; all-null column -> 'skip'."""
    if not rows:
        return []
    names = list(rows[0].keys())
    schema = []
    for name in names:
        kind = _column_kind(name, rows)
        schema.append((name, kind))
    return schema


def _column_kind(name, rows):
    vals = [r.get(name) for r in rows]
    non_null = [v for v in vals if v is not None]
    if not non_null:
        return "skip"
    # is it a list column?
    if any(isinstance(v, list) for v in non_null):
        elem = _elem_kind([e for v in non_null if isinstance(v, list) for e in v])
        return "a:" + elem
    # scalar: float beats int
    if any(isinstance(v, float) and not isinstance(v, bool) for v in non_null):
        return "f"
    if all(isinstance(v, (int, bool)) for v in non_null):
        return "i"
    if all(isinstance(v, str) for v in non_null):
        return "s"
    # mixed int/str shouldn't happen; prefer string
    return "s"


def _elem_kind(elems):
    non_null = [e for e in elems if e is not None]
    if not non_null:
        return "i"  # empty arrays everywhere: element type irrelevant (0 count)
    if any(isinstance(e, list) for e in non_null):
        inner = _elem_kind([x for e in non_null if isinstance(e, list) for x in e])
        return "a:" + inner
    if any(isinstance(e, float) and not isinstance(e, bool) for e in non_null):
        return "f"
    if all(isinstance(e, (int, bool)) for e in non_null):
        return "i"
    return "s"


# ---------- header ----------

def read_header(data):
    if data[:20] != MAGIC:
        raise ValueError("bad magic: %r" % data[:20])
    version = chr(data[20])
    rowcount = struct.unpack_from("<i", data, 21)[0]
    colcount = struct.unpack_from("<i", data, 25)[0]
    return version, rowcount, colcount


# ---------- localization (ver '6') ----------

def parse_localization(path):
    """Return {stringId(int): text(str)} for a ver-'6' language table."""
    data = open(path, "rb").read()
    version, rowcount, colcount = read_header(data)
    if version != "6":
        raise ValueError("not a localization table (version %r)" % version)
    index_off = struct.unpack_from("<i", data, 29)[0]
    count = struct.unpack_from("<i", data, index_off + 4)[0]
    out = {}
    o = index_off + 8
    for _ in range(count):
        sid = struct.unpack_from("<I", data, o)[0]
        pool_off = struct.unpack_from("<i", data, o + 4)[0]
        o += 8
        s, _ = _read_string(data, pool_off)
        out[sid] = s
    return out


# ---------- generic table parse (ver '0' / '1' / '2') ----------

def parse(path, schema):
    """Parse a ver-0/1/2 table. `schema` is [(name, kind)] (from infer_schema on
    the matching reference JSON). Returns {version, rowcount, colcount, columns,
    rows, bytes_consumed, file_size, clean}."""
    data = open(path, "rb").read()
    version, rowcount, colcount = read_header(data)
    names = [n for n, _ in schema]

    if version == "0":
        off = 29
        rows = []
        for _ in range(rowcount):
            row = {}
            for name, kind in schema:
                row[name], off = _read_value(data, off, kind)
            rows.append(row)
        consumed = off

    elif version == "1":
        off = 29
        rows = []
        for _ in range(rowcount):
            mask = int.from_bytes(data[off:off + 8], "little"); off += 8
            row = {}
            for i, (name, kind) in enumerate(schema):
                if kind == "skip":
                    row[name] = None
                    continue
                if (mask >> i) & 1:
                    row[name], off = _read_value(data, off, kind)
                else:
                    row[name] = _default_for(kind)
            rows.append(row)
        consumed = off

    elif version == "2":
        dict_off = struct.unpack_from("<i", data, 29)[0]
        off = 33
        pk_name, pk_kind = schema[0]
        body = schema[1:]  # primary key omitted from each row
        rows = []
        row_offsets = []
        for _ in range(rowcount):
            row_offsets.append(off)
            row = {}
            for name, kind in body:
                row[name], off = _read_value(data, off, kind)
            rows.append(row)
        rows_end = off
        # trailing dict: (pkey, absolute row offset)
        o = dict_off
        off_to_pk = {}
        for _ in range(rowcount):
            pk = struct.unpack_from("<i", data, o)[0]
            rbo = struct.unpack_from("<i", data, o + 4)[0]
            o += 8
            off_to_pk[rbo] = pk
        for row, ro in zip(rows, row_offsets):
            row[pk_name] = off_to_pk.get(ro)
        # reorder so pk is first
        rows = [{pk_name: r[pk_name], **{k: r[k] for k in names if k != pk_name}} for r in rows]
        consumed = rows_end
        return {
            "version": version, "rowcount": rowcount, "colcount": colcount,
            "columns": names, "rows": rows,
            "rows_end": rows_end, "dict_offset": dict_off,
            "clean": rows_end == dict_off, "file_size": len(data),
        }
    else:
        raise ValueError("parse() does not handle version %r (table %s)" % (version, path))

    return {
        "version": version, "rowcount": rowcount, "colcount": colcount,
        "columns": names, "rows": rows,
        "bytes_consumed": consumed, "file_size": len(data),
        "clean": consumed == len(data),
    }


def parse_with_reference(bin_path, reference_json_path):
    """Convenience: infer the schema from a reference JSON, then parse the bin."""
    ref = json.load(open(reference_json_path))
    schema = infer_schema(ref)
    return parse(bin_path, schema), schema
