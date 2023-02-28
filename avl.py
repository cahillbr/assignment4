# Name:
# OSU Email:
# Course: CS261 - Data Structures
# Assignment:
# Due Date:
# Description:


import random
from queue_and_stack import Queue, Stack
from bst import BSTNode, BST


class AVLNode(BSTNode):
    """
    AVL Tree Node class. Inherits from BSTNode
    DO NOT CHANGE THIS CLASS IN ANY WAY
    """
    def __init__(self, value: object) -> None:
        """
        Initialize a new AVL node
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        # call __init__() from parent class
        super().__init__(value)

        # new variables needed for AVL
        self.parent = None
        self.height = 0

    def __str__(self) -> str:
        """
        Override string method
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return 'AVL Node: {}'.format(self.value)


class AVL(BST):
    """
    AVL Tree class. Inherits from BST
    """

    def __init__(self, start_tree=None) -> None:
        """
        Initialize a new AVL Tree
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        # call __init__() from parent class
        super().__init__(start_tree)

    def __str__(self) -> str:
        """
        Override string method
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        values = []
        super()._str_helper(self._root, values)
        return "AVL pre-order { " + ", ".join(values) + " }"

    def is_valid_avl(self) -> bool:
        """
        Perform pre-order traversal of the tree. Return False if there
        are any problems with attributes of any of the nodes in the tree.

        This is intended to be a troubleshooting 'helper' method to help
        find any inconsistencies in the tree after the add() or remove()
        operations. Review the code to understand what this method is
        checking and how it determines whether the AVL tree is correct.

        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        stack = Stack()
        stack.push(self._root)
        while not stack.is_empty():
            node = stack.pop()
            if node:
                # check for correct height (relative to children)
                left = node.left.height if node.left else -1
                right = node.right.height if node.right else -1
                if node.height != 1 + max(left, right):
                    return False

                if node.parent:
                    # parent and child pointers are in sync
                    if node.value < node.parent.value:
                        check_node = node.parent.left
                    else:
                        check_node = node.parent.right
                    if check_node != node:
                        return False
                else:
                    # NULL parent is only allowed on the root of the tree
                    if node != self._root:
                        return False
                stack.push(node.right)
                stack.push(node.left)
        return True

    # ------------------------------------------------------------------ #

    def insert(self, value: object) -> AVLNode:
        """
        Inserts a new node with the given value in the tree.
        Returns the newly inserted node.
        """
        if self._root is None:
            self._root = AVLNode(value)
            return self._root

        # find the position to insert the new node
        parent = None
        curr = self._root
        while curr is not None:
            if value == curr.value:
                # node with the same value already exists
                return curr

            parent = curr
            if value < curr.value:
                curr = curr.left
            else:
                curr = curr.right

        # create the new node
        new_node = AVLNode(value)
        new_node.parent = parent

        # insert the new node as a child of parent
        if value < parent.value:
            parent.left = new_node
        else:
            parent.right = new_node

        return new_node

    def add(self, value: object) -> None:
        """
        Adds a new value to the tree while maintaining its AVL property.
        Duplicate values are not allowed. If the value is already in the
        tree, the method should not change the tree.
        """
        # insert the new node into the tree
        new_node = self.insert(value)
        if new_node is None:
            # node with the same value already exists
            return

        # update the heights of all the ancestors of the new node
        curr = new_node.parent
        while curr is not None:
            left_height = curr.left.height if curr.left else -1
            right_height = curr.right.height if curr.right else -1
            curr.height = 1 + max(left_height, right_height)

            # check the balance factor of the current node
            balance_factor = left_height - right_height
            if balance_factor > 1:
                # left-heavy
                if value < curr.left.value:
                    # left-left case
                    self._rotate_right(curr)
                else:
                    # left-right case
                    self._rotate_left(curr.left)
                    self._rotate_right(curr)
            elif balance_factor < -1:
                # right-heavy
                if value > curr.right.value:
                    # right-right case
                    self._rotate_left(curr)
                else:
                    # right-left case
                    self._rotate_right(curr.right)
                    self._rotate_left(curr)

            curr = curr.parent

        # check if the tree is still a valid AVL tree
        assert self.is_valid_avl()

    def _rotate_left(self, node: AVLNode) -> None:
        pivot = node.right
        if pivot:
            node.right = pivot.left
            if node.right:
                node.right.parent = node
            pivot.left = node
            pivot.parent = node.parent
            node.parent = pivot
            if node == self._root:
                self._root = pivot
            node.height = 1 + max(node.left_height(), node.right_height())
            pivot.height = 1 + max(pivot.left_height(), pivot.right_height())


    def remove(self, value: object) -> bool:
        """
        Remove value from the AVL tree if it exists. Return True if removed,
        False otherwise.
        """
        # Find the node to remove
        node = self._find_node(self._root, value)

        if node is None:
            # Value not found in the tree
            return False

        # Removing a node with two children
        if node.left and node.right:
            # Find the inorder successor of the node
            successor = self._find_min(node.right)
            # Copy the value of the successor to the node
            node.value = successor.value
            # Remove the successor node
            node = successor

        # Removing a node with one or no children
        if node.left:
            child = node.left
        else:
            child = node.right

        # Remove the node from the tree
        self._remove_node(node)

        # Update heights and balance factors of all ancestors of the deleted node
        self._update_heights_and_balance_factors(self._root)

        # Re-balance the tree if necessary
        self._rebalance(node.parent)

        return True

    def _update_heights_and_balance_factors(self, node: AVLNode) -> None:
        """
        Update heights and balance factors of all nodes in the tree starting
        from the given node and going up to the root.
        """
        if node is None:
            return

        # Update height of the node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # Update balance factor of the node
        node.balance_factor = self._get_height(node.right) - self._get_height(node.left)

        # Recursively update heights and balance factors of ancestors
        self._update_heights_and_balance_factors(node.parent)

    def _rebalance(self, node: AVLNode) -> None:
        """
        Re-balance the tree starting from the given node and going up to the root.
        """
        while node is not None:
            # Check if node is unbalanced
            if abs(node.balance_factor) > 1:
                # Node is left-heavy
                if node.balance_factor < 0:
                    # Node's left child is left-heavy
                    if node.left.balance_factor <= 0:
                        # LL case: rotate right
                        self._rotate_right(node)
                    # Node's left child is right-heavy
                    else:
                        # LR case: rotate left, then right
                        self._rotate_left(node.left)
                        self._rotate_right(node)
                # Node is right-heavy
                else:
                    # Node's right child is right-heavy
                    if node.right.balance_factor >= 0:
                        # RR case: rotate left
                        self._rotate_left(node)
                    # Node's right child is left-heavy
                    else:
                        # RL case: rotate right, then left
                        self._rotate_right(node.right)
                        self._rotate_left(node)

# ------------------- BASIC TESTING -----------------------------------------


if __name__ == '__main__':

    print("\nPDF - method add() example 1")
    print("----------------------------")
    test_cases = (
        (1, 2, 3),  # RR
        (3, 2, 1),  # LL
        (1, 3, 2),  # RL
        (3, 1, 2),  # LR
    )
    for case in test_cases:
        tree = AVL(case)
        print(tree)

    print("\nPDF - method add() example 2")
    print("----------------------------")
    test_cases = (
        (10, 20, 30, 40, 50),   # RR, RR
        (10, 20, 30, 50, 40),   # RR, RL
        (30, 20, 10, 5, 1),     # LL, LL
        (30, 20, 10, 1, 5),     # LL, LR
        (5, 4, 6, 3, 7, 2, 8),  # LL, RR
        (range(0, 30, 3)),
        (range(0, 31, 3)),
        (range(0, 34, 3)),
        (range(10, -10, -2)),
        ('A', 'B', 'C', 'D', 'E'),
        (1, 1, 1, 1),
    )
    for case in test_cases:
        tree = AVL(case)
        print('INPUT  :', case)
        print('RESULT :', tree)

    print("\nPDF - method add() example 3")
    print("----------------------------")
    for _ in range(100):
        case = list(set(random.randrange(1, 20000) for _ in range(900)))
        tree = AVL()
        for value in case:
            tree.add(value)
        if not tree.is_valid_avl():
            raise Exception("PROBLEM WITH ADD OPERATION")
    print('add() stress test finished')

    print("\nPDF - method remove() example 1")
    print("-------------------------------")
    test_cases = (
        ((1, 2, 3), 1),  # no AVL rotation
        ((1, 2, 3), 2),  # no AVL rotation
        ((1, 2, 3), 3),  # no AVL rotation
        ((50, 40, 60, 30, 70, 20, 80, 45), 0),
        ((50, 40, 60, 30, 70, 20, 80, 45), 45),  # no AVL rotation
        ((50, 40, 60, 30, 70, 20, 80, 45), 40),  # no AVL rotation
        ((50, 40, 60, 30, 70, 20, 80, 45), 30),  # no AVL rotation
    )
    for case, del_value in test_cases:
        tree = AVL(case)
        print('INPUT  :', tree, "DEL:", del_value)
        tree.remove(del_value)
        print('RESULT :', tree)

    print("\nPDF - method remove() example 2")
    print("-------------------------------")
    test_cases = (
        ((50, 40, 60, 30, 70, 20, 80, 45), 20),  # RR
        ((50, 40, 60, 30, 70, 20, 80, 15), 40),  # LL
        ((50, 40, 60, 30, 70, 20, 80, 35), 20),  # RL
        ((50, 40, 60, 30, 70, 20, 80, 25), 40),  # LR
    )
    for case, del_value in test_cases:
        tree = AVL(case)
        print('INPUT  :', tree, "DEL:", del_value)
        tree.remove(del_value)
        print('RESULT :', tree)

    print("\nPDF - method remove() example 3")
    print("-------------------------------")
    case = range(-9, 16, 2)
    tree = AVL(case)
    for del_value in case:
        print('INPUT  :', tree, del_value)
        tree.remove(del_value)
        print('RESULT :', tree)

    print("\nPDF - method remove() example 4")
    print("-------------------------------")
    case = range(0, 34, 3)
    tree = AVL(case)
    for _ in case[:-2]:
        root_value = tree.get_root().value
        print('INPUT  :', tree, root_value)
        tree.remove(root_value)
        print('RESULT :', tree)

    print("\nPDF - method remove() example 5")
    print("-------------------------------")
    for _ in range(100):
        case = list(set(random.randrange(1, 20000) for _ in range(900)))
        tree = AVL(case)
        for value in case[::2]:
            tree.remove(value)
        if not tree.is_valid_avl():
            raise Exception("PROBLEM WITH REMOVE OPERATION")
    print('remove() stress test finished')

    print("\nPDF - method contains() example 1")
    print("---------------------------------")
    tree = AVL([10, 5, 15])
    print(tree.contains(15))
    print(tree.contains(-10))
    print(tree.contains(15))

    print("\nPDF - method contains() example 2")
    print("---------------------------------")
    tree = AVL()
    print(tree.contains(0))

    print("\nPDF - method inorder_traversal() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print(tree.inorder_traversal())

    print("\nPDF - method inorder_traversal() example 2")
    print("---------------------------------")
    tree = AVL([8, 10, -4, 5, -1])
    print(tree.inorder_traversal())

    print("\nPDF - method find_min() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print(tree)
    print("Minimum value is:", tree.find_min())

    print("\nPDF - method find_min() example 2")
    print("---------------------------------")
    tree = AVL([8, 10, -4, 5, -1])
    print(tree)
    print("Minimum value is:", tree.find_min())

    print("\nPDF - method find_max() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print(tree)
    print("Maximum value is:", tree.find_max())

    print("\nPDF - method find_max() example 2")
    print("---------------------------------")
    tree = AVL([8, 10, -4, 5, -1])
    print(tree)
    print("Maximum value is:", tree.find_max())

    print("\nPDF - method is_empty() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print("Tree is empty:", tree.is_empty())

    print("\nPDF - method is_empty() example 2")
    print("---------------------------------")
    tree = AVL()
    print("Tree is empty:", tree.is_empty())

    print("\nPDF - method make_empty() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print("Tree before make_empty():", tree)
    tree.make_empty()
    print("Tree after make_empty(): ", tree)

    print("\nPDF - method make_empty() example 2")
    print("---------------------------------")
    tree = AVL()
    print("Tree before make_empty():", tree)
    tree.make_empty()
    print("Tree after make_empty(): ", tree)
