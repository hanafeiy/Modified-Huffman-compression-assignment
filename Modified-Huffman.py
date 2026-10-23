import json
from collections import Counter
from file_handler import read_file, write_file

# =====================================================================
#  Modified Huffman coding (compression + decompression)
#  Idea: symbols that are too rare (probability <= min_prob) are NOT given
#  their own Huffman code. They all share ONE special symbol ("Others"),
#  and after that symbol we write the rare symbol's fixed-length code.
# =====================================================================

OTHERS = 256  # one special symbol that stands for ALL the rare symbols


def code_length(k):
    """Bits needed for a fixed-length code for k symbols (9 symbols -> 4 bits)"""
    return max(1, (k - 1).bit_length())


# ---------------------------------------------------------------------
#  Diagnostics: size comparison report
# ---------------------------------------------------------------------
def print_size_report(title, before_label, before_bits, after_label, after_bits,
                      ratio_label="Compressed / Original"):
    """Prints a before/after size comparison.

    before_bits / after_bits are sizes in BITS (bytes = bits / 8).
    If the result is bigger than the input, "Saved" is shown as an increase.
    """
    before_bytes = before_bits / 8
    after_bytes = after_bits / 8

    print("\n--- %s ---" % title)
    print("%-22s: %d bits (%s Bytes)" % (before_label, before_bits, before_bytes))
    print("%-22s: %d bits (%s Bytes)" % (after_label, after_bits, after_bytes))

    if before_bits == 0:                      # empty input -> avoid dividing by zero
        print("Ratio can't be computed (empty input)")
        return

    ratio = after_bits / before_bits * 100    # new size as a % of the old size
    saved = 100 - ratio                       # positive = smaller, negative = bigger

    print("%-22s: %.1f%%" % (ratio_label, ratio))
    if saved >= 0:
        print("%-22s: %.1f%%" % ("Saved", saved))
    else:
        print("%-22s: %.1f%%  (became BIGGER)" % ("Increased by", -saved))


# Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud--Mahmoud
def huffman_codes(counts):
    """counts = {symbol: count}  ->  {symbol: Huffman code}"""
    # every node = [count, {symbol: code so far}]
    nodes = [[c, {s: ""}] for s, c in counts.items()]

    if len(nodes) == 0:
        return {}
    if len(nodes) == 1:                       # only one symbol -> give it code "0"
        return {s: "0" for s in counts}

    while len(nodes) > 1:
        # التعديل 1: الترتيب تنازلي (زي السلايدز بالظبط)
        nodes.sort(key=lambda n: n[0], reverse=True)

        # بنشيل الأصغر (اللي في الآخر)
        small = nodes.pop()
        # بنشيل الأكبر (اللي في الأول)
        big = nodes.pop()

        # merge the two nodes: prepend a bit to every code inside each of them
        merged = {}
        for s in big[1]:
            merged[s] = "0" + big[1][s]      # الرمز الأكبر ياخد 0
        for s in small[1]:
            merged[s] = "1" + small[1][s]    # الرمز الأصغر ياخد 1

        nodes.append([small[0] + big[0], merged])
    return nodes[0][1]


# AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR--AMIR
def compress(inp, out, min_prob):
    data = read_file(inp)
    counts = Counter(data)

    # fixed-length "original code" for each symbol in the file
    symbols = sorted(counts)
    n = code_length(len(symbols))

    # التعديل 2: عملنا Dictionary عشان نسرع البحث بدل .index()
    symbol_to_index = {s: i for i, s in enumerate(symbols)}

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
            # التعديل 3: استخدام الـ Dictionary بدل .index() لتوفير الوقت
            index = symbol_to_index[b]
            bits.append(format(index, "0%db" % n))  # + its original code
    bits = "".join(bits)

    # step 4: every 8 bits -> one real byte (last byte is padded with zeros)
    body = bytearray()
    for i in range(0, len(bits), 8):
        body.append(int(bits[i:i + 8].ljust(8, "0"), 2))

    # step 5: write header line (overhead) + the binary data
    header = json.dumps({"codes": codes, "symbols": symbols, "nbits": len(bits)})
    header_bytes = header.encode() + b"\n"
    write_file(out, header_bytes + bytes(body))

    # ---- diagnostics: compare sizes before / after compression ----
    original_bits = len(data) * 8                # each original symbol = 1 byte = 8 bits
    header_bits = len(header_bytes) * 8          # overhead needed to decode later

    # 1) the data itself only (the encoded bits, without the header)
    print_size_report("Size Comparison (data only)",
                      "Before (Original)", original_bits,
                      "After (Compressed)", len(bits))

    # 2) the real file on disk = header + data (padding included)
    print_size_report("Size Comparison (whole file incl. header)",
                      "Before (Original)", original_bits,
                      "After (Compressed)", header_bits + len(body) * 8)
    print("Header overhead       : %d bits (%s Bytes)" % (header_bits, header_bits / 8))


# Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen--Nermeen
def decompress(inp, out):
    raw = read_file(inp)
    header_line, body = raw.split(b"\n", 1)      # first line = header, rest = data
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

    write_file(out, result)
    print("Decompression done")

    # ---- diagnostics: compare sizes before / after decompression ----
    # Before = the compressed file (header + data), After = the restored file
    print_size_report("Size Comparison (decompression)",
                      "Before (Compressed)", len(raw) * 8,
                      "After (Decompressed)", len(result) * 8,
                      ratio_label="Decompressed / Compressed")


# ---------------------------------------------------------------------
#  Main: ask the user what to do
# ---------------------------------------------------------------------
mode = input("Compress or Decompress? (c/d): ").strip().lower()
inp = input("Input file: ").strip()
out = input("Output file: ").strip()
if mode == "c":
    compress(inp, out, float(input("Minimum symbol probability (e.g. 0.05): ")))
else:
    decompress(inp, out)
