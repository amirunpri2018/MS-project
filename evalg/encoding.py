from GPy.kern.src.kern import Kern

from autoks.kernel import subkernel_expression

operators = ['+', '*']


def val_to_label(value):
    if isinstance(value, Kern):
        return subkernel_expression(value)
    else:
        return str(value)


class TreeNode:
    def __init__(self, value, parent=None):
        self._value = value
        self.label = val_to_label(value)
        self.parent = parent

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        # update label as well
        self.label = val_to_label(value)

    def __str__(self):
        return self.label


class BinaryTreeNode(TreeNode):

    def __init__(self, value, parent=None):
        super().__init__(value, parent)

        self.left = None
        self.right = None

    def add_left(self, val):
        self.left = BinaryTreeNode(val, self)
        return self.left

    def add_right(self, val):
        self.right = BinaryTreeNode(val, self)
        return self.right

    def create_graph(self, graph=None):
        root = self
        if not graph:
            from graphviz import Digraph
            graph = Digraph()

        if root is not None:
            root_id = str(id(root))
            graph.node(root_id, label=root.label)

            if root.left is not None:
                left = root.left
                left_id = str(id(left))
                graph.node(left_id, label=left.label)
                graph.edge(root_id, left_id)
                root.left.create_graph(graph=graph)
            if root.right is not None:
                right = root.right
                right_id = str(id(right))
                graph.node(right_id, label=right.label)
                graph.edge(root_id, right_id)
                root.right.create_graph(graph=graph)

        return graph

    def __str__(self):
        return self.label


class BinaryTree:

    def __init__(self):
        self.root = None

    def create_graph(self):
        return self.root.create_graph()

    def select_postorder(self, node_idx):
        """ Select node from binary tree given postorder index
        """
        node = self.root
        stack = []
        last_node_visited = None
        i = 0
        while len(stack) > 0 or node is not None:
            if node:
                stack.append(node)
                node = node.left
            else:
                peek_node = stack[-1]
                if peek_node.right is not None and last_node_visited is not peek_node.right:
                    node = peek_node.right
                else:
                    if i == node_idx:
                        return peek_node
                    last_node_visited = stack.pop()
                    i += 1

        return None

    def infix(self):
        return self._infix_helper(self.root)

    def _infix_helper(self, root, expression=None):
        if expression is None:
            expression = ''

        if root is not None:
            if root.value in operators:
                expression += '('

            expression += self._infix_helper(root.left)
            expression += root.label
            expression += self._infix_helper(root.right)

            if root.value in operators:
                expression += ')'

        return expression


def postfix_tokens_to_binexp_tree(postfix_tokens):
    tree = BinaryTree()

    root = BinaryTreeNode(postfix_tokens[-1])
    tree.root = root

    curr = root
    for token in postfix_tokens[-2::-1]:
        # while curr can't have more children
        while curr.value not in operators or (curr.right is not None and curr.left is not None):
            curr = curr.parent

        if curr.right is None:
            node = curr.add_right(token)
        elif curr.left is None:
            node = curr.add_left(token)
        curr = node

    return tree


def infix_tokens_to_postfix_tokens(infix_tokens):
    pemdas = {}
    pemdas["*"] = 3
    pemdas["+"] = 1
    pemdas["("] = 0

    operator_stack = []
    postfix_tokens = []
    for token in infix_tokens:
        if token in operators:
            while len(operator_stack) is not 0 and pemdas[operator_stack[-1]] >= pemdas[token]:
                postfix_tokens.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            top_token = operator_stack.pop()
            while top_token != '(':
                postfix_tokens.append(top_token)
                top_token = operator_stack.pop()
        else:
            # token is an operand
            postfix_tokens.append(token)

    while len(operator_stack) > 0:
        postfix_tokens.append(operator_stack.pop())

    return postfix_tokens
