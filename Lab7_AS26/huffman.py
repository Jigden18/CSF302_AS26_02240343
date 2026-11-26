# Q2: Huffman Coding — build tree with a priority queue, code table, encode/decode, compression ratio
#
# Usage:
#   python huffman.py                     -> everything
#   python huffman.py table [file]        -> code table + encode/decode check (default data/english_text.txt)
#   python huffman.py compare [files...]  -> compression ratio vs 8-bit fixed length (default: the 3 sample files)

import heapq
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = [os.path.join(HERE, "data", f) for f in ("english_text.txt", "python_code.txt", "dna_sequence.txt")]


class Node:
    def __init__(self, freq, char=None, left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None


def char_frequencies(text):
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    return freq


# ---------------------------------------------------------------------------
# Build the Huffman tree: repeatedly merge the two least frequent nodes
# (min-heap; the counter breaks ties so nodes are never compared directly)
# ---------------------------------------------------------------------------
def build_tree(freq):
    heap = []
    counter = 0
    for ch, f in sorted(freq.items()):
        heap.append((f, counter, Node(f, ch)))
        counter += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, counter, Node(f1 + f2, left=a, right=b)))
        counter += 1
    return heap[0][2]


def build_codes(node, prefix="", table=None):
    if table is None:
        table = {}
    if node.is_leaf():
        table[node.char] = prefix or "0"          # one distinct character -> code "0"
    else:
        build_codes(node.left, prefix + "0", table)
        build_codes(node.right, prefix + "1", table)
    return table


def encode(text, codes):
    return "".join(codes[ch] for ch in text)


def decode(bits, root):
    if root.is_leaf():                          # only one distinct character
        return root.char * len(bits)
    out, node = [], root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.is_leaf():
            out.append(node.char)
            node = root
    return "".join(out)


def show_char(ch):
    return {" ": "' '", "\n": "\\n", "\t": "\\t"}.get(ch, ch)


def huffman(text):
    root = build_tree(char_frequencies(text))
    codes = build_codes(root)
    bits = encode(text, codes)
    return root, codes, bits


# ---------------------------------------------------------------------------
# Code table for one file
# ---------------------------------------------------------------------------
def table_demo(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    freq = char_frequencies(text)
    root, codes, bits = huffman(text)
    print(f"=== Huffman code table for {os.path.basename(path)} ===")
    print(f"{len(text):,} characters, {len(freq)} distinct\n")
    rows = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    half = (len(rows) + 1) // 2
    head = f"{'Char':>5} {'Freq':>5}  {'Code':<14}"
    print(head + "   |" + head)
    print("-" * (len(head) * 2 + 4))
    for r in range(half):
        cells = []
        for ch, f in rows[r::half][:2]:
            cells.append(f"{show_char(ch):>5} {f:>5}  {codes[ch]:<14}")
        print("   |".join(cells))

    decoded = decode(bits, root)
    print(f"\nEncoded bit string (first 80 of {len(bits):,} bits):")
    print("  " + bits[:80] + "...")
    print(f"Decoded text equals original: {decoded == text}")
    print(f"Huffman: {len(bits):,} bits  vs  8-bit fixed length: {8 * len(text):,} bits  "
          f"-> {len(bits) / (8 * len(text)) * 100:.1f}% of the original size")
    print()


# ---------------------------------------------------------------------------
# Compression ratio for several files
# ---------------------------------------------------------------------------
def compare(paths):
    print("=== Compression ratio: Huffman vs 8-bit fixed-length encoding ===")
    print(f"{'File':<18} | {'Chars':>7} | {'Distinct':>8} | {'Fixed bits':>10} | {'Huffman bits':>12} | "
          f"{'Bits/char':>9} | {'Ratio':>6} | {'Saved':>6} | decoded ok")
    print("-" * 110)
    for path in paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        root, codes, bits = huffman(text)
        ok = decode(bits, root) == text
        fixed = 8 * len(text)
        ratio = len(bits) / fixed
        print(f"{os.path.basename(path):<18} | {len(text):>7,} | {len(codes):>8} | {fixed:>10,} | {len(bits):>12,} | "
              f"{len(bits) / len(text):>9.3f} | {ratio * 100:>5.1f}% | {(1 - ratio) * 100:>5.1f}% | {ok}")
    print("\nRatio = Huffman bits / fixed bits (lower is better). The code table itself is not counted.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("table", "all"):
        table_demo(sys.argv[2] if arg == "table" and len(sys.argv) > 2 else SAMPLES[0])
    if arg in ("compare", "all"):
        compare(sys.argv[2:] if arg == "compare" and len(sys.argv) > 2 else SAMPLES)
    if arg not in ("table", "compare", "all"):
        print("Unknown option. Use: table [file] | compare [files...]")


# Analysis / Conclusion:
# Huffman coding gives frequent characters short codes and rare characters long
# ones. Because the codes come from the leaves of a binary tree, no code is a
# prefix of another, so the bit string can be decoded without separators, and
# the decoded text matches the original exactly for every file.
#
# How much it saves depends on how skewed the character frequencies are and how
# many distinct characters there are. English text and source code use around
# 40-60 distinct characters with very uneven frequencies (space, e, t, ...), so
# they need roughly 4.3-4.6 bits per character instead of 8. The DNA file uses
# only 4 letters (plus newlines), so it needs about 2 bits per character and is
# compressed the most. The size of the code table is not included; for short
# files it would reduce the saving slightly.
