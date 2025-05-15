# huffman.py

import heapq
import pickle
from utils import read_text_file, write_binary_file, write_text_file, log_info, log_error

class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text: str) -> dict:
    """
    Build a frequency table (char -> count) from the input text.
    """
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    return freq


def build_huffman_tree(freq_table: dict) -> Node:
    """
    Build the Huffman tree using a min-heap. Returns the root node.
    """
    heap = [Node(char, f) for char, f in freq_table.items()]
    heapq.heapify(heap)

    # Edge case: only one unique character
    if len(heap) == 1:
        only = heapq.heappop(heap)
        root = Node(None, only.freq)
        root.left = only
        return root

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]


def generate_codes(root: Node) -> dict:
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Returns a dict: char -> code (as string of '0'/'1').
    """
    codes = {}

    def _walk(node: Node, code: str):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = code
            return
        _walk(node.left, code + '0')
        _walk(node.right, code + '1')

    _walk(root, '')
    return codes


def compress(text: str) -> tuple:
    """
    Compress input text. Returns (data_bytes, codes, padding).
    """
    freq_table = build_frequency_table(text)
    root = build_huffman_tree(freq_table)
    codes = generate_codes(root)
    encoded = ''.join(codes[ch] for ch in text)

    # Pad to full bytes
    padding = (8 - len(encoded) % 8) % 8
    encoded += '0' * padding

    data = bytearray()
    for i in range(0, len(encoded), 8):
        byte = encoded[i:i+8]
        data.append(int(byte, 2))

    return data, codes, padding


def decompress(data_bytes: bytearray, codes: dict, padding: int) -> str:
    """
    Decompress data_bytes using codes and padding. Returns the original text.
    """
    # Reverse lookup
    rev = {code: ch for ch, code in codes.items()}

    bit_str = ''.join(f"{b:08b}" for b in data_bytes)
    if padding:
        bit_str = bit_str[:-padding]

    result = []
    curr = ''
    for bit in bit_str:
        curr += bit
        if curr in rev:
            result.append(rev[curr])
            curr = ''

    return ''.join(result)


def compress_file(input_path: str, output_path: str) -> None:
    """
    Read text from input_path, compress it, and write to output_path.
    """
    try:
        text = read_text_file(input_path)
        data, codes, padding = compress(text)
        header = pickle.dumps((codes, padding))
        write_binary_file(output_path, header + data)
        log_info(f"Compressed '{input_path}' → '{output_path}' ({len(data)} bytes)")
    except Exception as e:
        log_error(f"Compression failed for '{input_path}': {e}")


def decompress_file(input_path: str, output_path: str) -> None:
    """
    Read compressed file from input_path and write decompressed text to output_path.
    """
    try:
        with open(input_path, 'rb') as f:
            codes, padding = pickle.load(f)
            data = f.read()
        text = decompress(data, codes, padding)
        write_text_file(output_path, text)
        log_info(f"Decompressed '{input_path}' → '{output_path}' ({len(text)} chars)")
    except Exception as e:
        log_error(f"Decompression failed for '{input_path}': {e}")
