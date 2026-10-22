import json
from collections import Counter
#Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud

OTHERS = 256  # one special symbol that stands for ALL the rare symbols
def code_length(k):
    """Bits needed for a fixed-length code for k symbols (9 symbols -> 4 bits)"""
    return max(1, (k - 1).bit_length())


def huffman_codes(counts):
    """counts = {symbol: count}  ->  {symbol: Huffman code}"""
    # every node = [count, {symbol: code so far}]
    nodes = [[c, {s: ""}] for s, c in counts.items()]

    if len(nodes) == 0:
        return {}
    if len(nodes) == 1:
        return {s: "0" for s in counts}

    while len(nodes) > 1:
        nodes.sort(key=lambda n: n[0])  # smallest first
        small = nodes.pop(0)            # take the two smallest nodes
        big = nodes.pop(0)
        merged = {}
        for s in big[1]:
            merged[s] = "0" + big[1][s]      # the bigger one gets 0
        for s in small[1]:
            merged[s] = "1" + small[1][s]    # the smaller one gets 1
        nodes.append([small[0] + big[0], merged])

    return nodes[0][1]



 # AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR
def compress(inp, out, min_prob):
    data = open(inp, "rb").read()
    counts = Counter(data)

    # fixed-length "original code" for each symbol in the file
    symbols = sorted(counts)
    n = code_length(len(symbols))

    # step 1: symbols with probability <= min_prob go to the "Others" group
    freq = {}
    others = 0
    for s, c in counts.items():
        if c / len(data) <= min_prob:
            others += c
        else:
            freq[s] = c
    if others > 0:
        freq[OTHERS] = others

    # step 2: build Huffman codes
    codes = huffman_codes(freq)

    # step 3: replace every symbol with its code (as a text of 0s and 1s)
    bits = []
    for b in data:
        if b in codes:
            bits.append(codes[b])
        else:                                    # rare symbol:
            bits.append(codes[OTHERS])           # "Others" code
            index = symbols.index(b)
            bits.append(format(index, "0%db" % n))  # + its original code
    bits = "".join(bits)

    # step 4: every 8 bits -> one real byte (last byte is padded with zeros)
    body = bytearray()
    for i in range(0, len(bits), 8):
        body.append(int(bits[i:i + 8].ljust(8, "0"), 2))

    # step 5: write header line (overhead) + the binary data
    header = json.dumps({"codes": codes, "symbols": symbols, "nbits": len(bits)})
    with open(out, "wb") as f:
        f.write(header.encode() + b"\n" + bytes(body))

    print("Original:", len(data), "bytes | Compressed:", len(body), "bytes |", len(bits), "bits")
    if len(body) > 0:
        print("Compression ratio:", round(len(data) / len(body), 3))




#Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen
def decompress(inp, out):
    raw = open(inp, "rb").read()
    header_line, body = raw.split(b"\n", 1)
    header = json.loads(header_line)

    decode_table = {code: int(s) for s, code in header["codes"].items()}  # code -> symbol
    symbols = header["symbols"]
    n = code_length(len(symbols))

    # bytes -> bits, then cut the padding using nbits
    bits = "".join(format(b, "08b") for b in body)[:header["nbits"]]

    result = bytearray()
    cur = ""
    i = 0
    while i < len(bits):
        cur += bits[i]            # read one bit
        i += 1
        if cur in decode_table:   # we found a complete code
            symbol = decode_table[cur]
            if symbol == OTHERS:  # next n bits = original code of the symbol
                result.append(symbols[int(bits[i:i + n], 2)])
                i += n
            else:
                result.append(symbol)
            cur = ""

    with open(out, "wb") as f:
        f.write(result)
    print("Decompression done")


mode = input("Compress or Decompress? (c/d): ").strip().lower()
inp = input("Input file: ").strip()
out = input("Output file: ").strip()
if mode == "c":
    compress(inp, out, float(input("Minimum symbol probability (e.g. 0.05): ")))
else:
    decompress(inp, out)
