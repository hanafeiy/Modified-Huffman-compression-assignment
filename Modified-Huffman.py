import json
from collections import Counter

 # AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR

ESC = 256  # one special symbol that stands for ALL the rare bytes
def make_codes(freq):
    """Takes {symbol: count} and returns {symbol: Huffman code}"""
    # each node = [count, {symbol: code}]  (codes start empty)
    nodes = [[f, {s: ""}] for s, f in freq.items()]

    if len(nodes) == 0:
        return {}
    if len(nodes) == 1:  # only one symbol in the file
        return {s: "0" for s in nodes[0][1]}

    while len(nodes) > 1:
        nodes.sort(key=lambda n: n[0])  # sort from smallest to largest count
        a = nodes.pop(0)                # take the two smallest nodes
        b = nodes.pop(0)
        merged = {}
        for s, c in a[1].items():
            merged[s] = "0" + c         # left side: put 0 in front
        for s, c in b[1].items():
            merged[s] = "1" + c         # right side: put 1 in front
        nodes.append([a[0] + b[0], merged])

    return nodes[0][1]

#Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud
def compress(inp, out, min_prob):
    data = open(inp, "rb").read()
    total = len(data)
    freq = Counter(data)

    # bytes with probability below the minimum are merged into ESC
    kept = {}
    esc = 0
    for s, f in freq.items():
        if f / total >= min_prob:
            kept[s] = f
        else:
            esc += f
    if esc > 0:
        kept[ESC] = esc

    codes = make_codes(kept)

    # convert the data to bits 
    bits = []
    for b in data:
        if b in codes:
            bits.append(codes[b])
        else:                              # rare byte
            bits.append(codes[ESC])        # ESC code first
            bits.append(format(b, "08b"))  # then the original byte as 8 bits
    bits = "".join(bits)

    # every 8 bits = one real byte (last one is padded with zeros)
    body = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8].ljust(8, "0")
        body.append(int(chunk, 2))

    # first line of the file = header (code table + real number of bits)
    header = json.dumps({"codes": codes, "nbits": len(bits)})
    with open(out, "wb") as f:
        f.write(header.encode() + b"\n")
        f.write(body)

    print("Original:", total, "bytes | Compressed:", len(body), "bytes (without header)")
    if len(body) > 0:
        print("Compression ratio:", round(total / len(body), 3))


#Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen

def decompress(inp, out):
    raw = open(inp, "rb").read()
    header_line, body = raw.split(b"\n", 1)
    header = json.loads(header_line)

    # reverse the table: code -> symbol
    rev = {code: int(s) for s, code in header["codes"].items()}

    # bytes -> bits, then remove the padding
    bits = "".join(format(b, "08b") for b in body)[:header["nbits"]]

    result = bytearray()
    cur = ""
    i = 0
    while i < len(bits):
        cur += bits[i]
        i += 1
        if cur in rev:                     # found a complete code
            sym = rev[cur]
            if sym == ESC:                 # the next 8 bits are the original byte
                result.append(int(bits[i:i + 8], 2))
                i += 8
            else:
                result.append(sym)
            cur = ""

    open(out, "wb").write(bytes(result))
    print("Decompression done")


mode = input("Compress or Decompress? (c/d): ").strip().lower()
inp = input("Input file: ").strip()
out = input("Output file: ").strip()
if mode == "c":
    compress(inp, out, float(input("Minimum symbol probability (e.g. 0.01): ")))
else:
    decompress(inp, out)