class Node:
    def __init__(self, value):
        self.left = None
        self.data = value
        self.right = None

class Tree:
    def createNode(self,data):
        return Node(data)

    def insert(self, node, data):
        if node is None:
            return self.createNode(data)
        if data < node.data:
            node.left = self.insert(node.left, data)
        else:
            node.right = self.insert(node.right,data)
        return node

    def traverse_inorder(self, root):
        if root is not None:
            self.traverse_inorder(root.left)
            print(root.data, end='')
            self.traverse_inorder(root.right)

    def traverse_preorder(self, root):
        if root is not None:
            print(root.data, end='')
            self.traverse_preorder(root.left)
            self.traverse_preorder(root.right)

    def traverse_postorder(self, root):
        if root is not None:
            self.traverse_postorder(root.left)
            self.traverse_postorder(root.right)
            print(root.data, end='')

    def height(self, root):
        if root is None:
            return -1
        return max(self.height(root.left), self.height(root.right)) + 1

## example
tree = Tree()
root = tree.createNode(5)
print(root.data)
tree.insert(root,2)
tree.insert(root,10)
tree.insert(root,7)
tree.insert(root,15)
tree.insert(root,12)
tree.insert(root,20)
tree.insert(root,30)
tree.insert(root,6)
tree.insert(root,8)
print('\nin order --------->')
tree.traverse_inorder(root)
print('\nin pre order --------->')
tree.traverse_preorder(root)
print('\nin post order --------->')
tree.traverse_postorder(root)
print('\nheight(',tree.height(root),')')
