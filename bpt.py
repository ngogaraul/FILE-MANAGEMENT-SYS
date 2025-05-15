"""
B+ Tree Module

Implements a B+ Tree for indexing filenames with the following algorithmic steps:

1. **Search**  
   • Descend from the root internal nodes by choosing the correct child pointer whose
     key range would include the target key.  
   • Once at a leaf, perform a linear scan of the leaf’s `keys` to match exactly.  

2. **Insert**  
   • Find the correct leaf via the same descent as in search.  
   • Insert the key/value into the leaf’s sorted arrays.  
   • If the leaf overflows (more than order–1 keys), split it around the median key and
     promote the first key of the new leaf to the parent.  
   • If an internal node overflows, split it similarly and propagate upward, possibly
     creating a new root.  

3. **List All (Range Scan)**  
   • Traverse to the leftmost leaf, then follow the `next` pointers across the
     leaf-linked list, collecting all (key, value) pairs in sorted order.  

Design Notes:  
- All actual data lives in leaves, so in-order traversal is simply a linked-list walk.  
- Splits maintain tree balance, guaranteeing height ≤ ⌈log₍⌈order/2⌉₎ N⌉.  
- Default order = 4 for simplicity; increase in production to match I/O block size.
"""

from utils import log_info, log_error

class BPlusNode:
    def __init__(self, order):
        self.order = order
        self.keys = []
        self.parent = None

class BPlusLeaf(BPlusNode):
    def __init__(self, order):
        super().__init__(order)
        self.values = []
        self.next = None

class BPlusInternal(BPlusNode):
    def __init__(self, order):
        super().__init__(order)
        self.children = []

class BPlusTree:
    def __init__(self, order=4):
        self.order = order
        self.root = BPlusLeaf(order)

    def search(self, key):
        try:
            leaf = self._find_leaf(self.root, key)
            for i, k in enumerate(leaf.keys):
                if k == key:
                    log_info(f"B+ Tree: found '{key}' → {leaf.values[i]}")
                    return leaf.values[i]
            log_info(f"B+ Tree: '{key}' not found")
            return None
        except Exception as e:
            log_error(f"B+ Tree search error: {e}")
            return None

    def insert(self, key, value):
        try:
            leaf = self._find_leaf(self.root, key)
            i = 0
            while i < len(leaf.keys) and key > leaf.keys[i]:
                i += 1
            if i < len(leaf.keys) and leaf.keys[i] == key:
                leaf.values[i] = value
                log_info(f"B+ Tree: updated '{key}'")
                return
            leaf.keys.insert(i, key)
            leaf.values.insert(i, value)
            if len(leaf.keys) > self.order - 1:
                self._split_leaf(leaf)
            log_info(f"B+ Tree: inserted '{key}'")
        except Exception as e:
            log_error(f"B+ Tree insert error: {e}")

    def list_all(self):
        """
        List all (filename, path) entries in sorted order.
        Returns a list of tuples: (key, value).
        """
        try:
            node = self.root
            # descend to leftmost leaf
            while not isinstance(node, BPlusLeaf):
                node = node.children[0]
            entries = []
            while node:
                for k, v in zip(node.keys, node.values):
                    entries.append((k, v))
                node = node.next
            log_info(f"B+ Tree: listed {len(entries)} indexed entries")
            return entries
        except Exception as e:
            log_error(f"B+ Tree list error: {e}")
            return []

    # ————— Helpers —————
    def _find_leaf(self, node, key):
        if isinstance(node, BPlusLeaf):
            return node
        for i, k in enumerate(node.keys):
            if key < k:
                return self._find_leaf(node.children[i], key)
        return self._find_leaf(node.children[-1], key)

    def _split_leaf(self, leaf):
        mid = (self.order + 1) // 2
        new_leaf = BPlusLeaf(self.order)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        new_leaf.parent = leaf.parent

        if leaf.parent is None:
            new_root = BPlusInternal(self.order)
            new_root.keys = [new_leaf.keys[0]]
            new_root.children = [leaf, new_leaf]
            leaf.parent = new_root
            new_leaf.parent = new_root
            self.root = new_root
        else:
            self._insert_internal(leaf.parent, new_leaf.keys[0], new_leaf)

    def _insert_internal(self, parent, key, child):
        i = 0
        while i < len(parent.keys) and key > parent.keys[i]:
            i += 1
        parent.keys.insert(i, key)
        parent.children.insert(i+1, child)
        child.parent = parent
        if len(parent.keys) > self.order - 1:
            self._split_internal(parent)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        split_key = node.keys[mid]
        new_node = BPlusInternal(self.order)
        new_node.keys = node.keys[mid+1:]
        new_node.children = node.children[mid+1:]
        for c in new_node.children:
            c.parent = new_node
        node.keys = node.keys[:mid]
        node.children = node.children[:mid+1]

        if node.parent is None:
            new_root = BPlusInternal(self.order)
            new_root.keys = [split_key]
            new_root.children = [node, new_node]
            node.parent = new_root
            new_node.parent = new_root
            self.root = new_root
        else:
            self._insert_internal(node.parent, split_key, new_node)
