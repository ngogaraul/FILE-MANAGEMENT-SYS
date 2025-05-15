# cli.py

import os
import sys
import pickle
from utils import log_info, log_error
from huffman import compress_file, decompress_file
from rbt import RedBlackTree
from bpt import BPlusTree

# File where the index (RB & B+ trees) is persisted
INDEX_FILE = 'index.dat'


def load_index():
    """
    Load the persisted index from disk if available, else create new trees.
    """
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'rb') as f:
                rbt, bpt = pickle.load(f)
            log_info(f"Loaded index from '{INDEX_FILE}'")
            return rbt, bpt
        except Exception as e:
            log_error(f"Failed to load index: {e}")
    # Create fresh trees if load failed or file missing
    return RedBlackTree(), BPlusTree(order=4)


def save_index(rbt, bpt):
    """
    Persist the current index trees to disk.
    """
    try:
        with open(INDEX_FILE, 'wb') as f:
            pickle.dump((rbt, bpt), f)
        log_info(f"Saved index to '{INDEX_FILE}'")
    except Exception as e:
        log_error(f"Failed to save index: {e}")


def menu():
    print("""
=== File Management System ===
1. Compress text file
2. Decompress file
3. Insert file into index
4. Search file in index
5. List all indexed files
6. Exit
""")


def main():
    log_info("Starting File Management CLI")
    # Load or initialize index structures
    rbt, bpt = load_index()

    try:
        while True:
            menu()
            choice = input("Select an option [1-6]: ").strip()

            if choice == '1':
                inp = input("Enter input text file path: ").strip()
                out = input("Enter output compressed path: ").strip()
                if os.path.isdir(out):
                    base = os.path.basename(inp)
                    name, _ = os.path.splitext(base)
                    out = os.path.join(out, name + '.huff')
                compress_file(inp, out)

            elif choice == '2':
                inp = input("Enter input compressed file path: ").strip()
                out = input("Enter output decompressed path: ").strip()
                if os.path.isdir(out):
                    base = os.path.basename(inp)
                    name, _ = os.path.splitext(base)
                    out = os.path.join(out, name + '_dec.txt')
                decompress_file(inp, out)

            elif choice == '3':
                name = input("Enter filename (key): ").strip()
                path = input("Enter file path (value): ").strip()
                rbt.insert(name, path)
                bpt.insert(name, path)
                print(f"Inserted '{name}' into index.")

            elif choice == '4':
                name = input("Enter filename to search: ").strip()
                r = rbt.search(name)
                b = bpt.search(name)
                print(f"[RB Tree] {'Found: ' + r if r else 'Not found.'}")
                print(f"[B+ Tree] {'Found: ' + b if b else 'Not found.'}")

            elif choice == '5':
                files = bpt.list_all()
                print("Indexed files:")
                for f in files:
                    print(" -", f)

            elif choice == '6':
                # Persist before exiting
                save_index(rbt, bpt)
                log_info("Exiting CLI")
                break

            else:
                print("Invalid choice. Try again.")

    except Exception as e:
        log_error(f"CLI encountered error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
