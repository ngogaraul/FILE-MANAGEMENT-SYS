# rbt.py

from utils import log_info, log_error

class RBNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.color = 'red'      # New nodes start red
        self.parent = None
        self.left = None
        self.right = None

class RedBlackTree:
    def __init__(self):
        self.NULL_LEAF = RBNode(None, None)
        self.NULL_LEAF.color = 'black'
        self.root = self.NULL_LEAF

    def insert(self, key, value):
        try:
            node = RBNode(key, value)
            node.left = node.right = self.NULL_LEAF
            parent = None
            cur = self.root
            while cur != self.NULL_LEAF:
                parent = cur
                if key < cur.key:
                    cur = cur.left
                elif key > cur.key:
                    cur = cur.right
                else:
                    cur.value = value
                    log_info(f"RB-Tree: updated '{key}'")
                    return
            node.parent = parent
            if parent is None:
                self.root = node
            elif key < parent.key:
                parent.left = node
            else:
                parent.right = node
            self._fix_insert(node)
            log_info(f"RB-Tree: inserted '{key}'")
        except Exception as e:
            log_error(f"RB-Tree insert error: {e}")

    def search(self, key):
        try:
            cur = self.root
            while cur != self.NULL_LEAF:
                if key == cur.key:
                    log_info(f"RB-Tree: found '{key}' → {cur.value}")
                    return cur.value
                cur = cur.left if key < cur.key else cur.right
            log_info(f"RB-Tree: '{key}' not found")
            return None
        except Exception as e:
            log_error(f"RB-Tree search error: {e}")
            return None

    # ————— Internal rotations and fix-up —————
    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NULL_LEAF:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NULL_LEAF:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def _fix_insert(self, k):
        while k.parent and k.parent.color == 'red':
            gp = k.parent.parent
            if k.parent == gp.left:
                uncle = gp.right
                if uncle and uncle.color == 'red':
                    k.parent.color = uncle.color = 'black'
                    gp.color = 'red'
                    k = gp
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self._rotate_left(k)
                    k.parent.color = 'black'
                    gp.color = 'red'
                    self._rotate_right(gp)
            else:
                uncle = gp.left
                if uncle and uncle.color == 'red':
                    k.parent.color = uncle.color = 'black'
                    gp.color = 'red'
                    k = gp
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self._rotate_right(k)
                    k.parent.color = 'black'
                    gp.color = 'red'
                    self._rotate_left(gp)
        self.root.color = 'black'
