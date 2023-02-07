from constraint import *


class DLXNode:
    """Base Class for a dancing links node"""

    def __init__(self, column, number: int) -> None:
        self.left: DLXNode = self       # Pointer to the node to the left
        self.right: DLXNode = self      # Pointer to the node to the right
        self.up: DLXNode = self         # Pointer to the node above
        self.down: DLXNode = self       # Pointer to the node below
        self.column: DLXColumn = column   # Pointer to the column header node
        self.number = number

    def insert_below(self, new_node):
        """Inserts the node `new_node` below this node"""

        new_node.up = self
        new_node.down = self.down
        self.down.up = new_node
        self.down = new_node

        self.column.size += 1

    def insert_right(self, new_node):
        """Inserts the node `new_node` to the right of this node"""

        new_node.left = self
        new_node.right = self.right
        self.right.left = new_node
        self.right = new_node

    def insert_left(self, new_node):
        """Inserts the node `new_node` to the right of this node"""

        new_node.right = self
        new_node.left = self.left
        self.left.right = new_node
        self.left = new_node

    def cover_row(self):
        """
        Loops over all the other nodes in this row and 'covers' them
        The current node is not covered as it is in a covered column
        """

        current = self
        while (current := current.right) != self:
            current.up.down = current.down
            current.down.up = current.up
            current.column.size -= 1

    def uncover_row(self):
        """
        Loops over all other nodes in this row and 'uncovers' them
        This is done in the reverse order they were 'covered'
        """

        current = self
        while (current := current.left) != self:
            current.up.down = current
            current.down.up = current
            current.column.size += 1


class DLXColumn(DLXNode):
    """Dancing links column header node"""

    def __init__(self, constraint: Constraint) -> None:
        super().__init__(self, 0)
        self.size: int = 0      # The number of nodes in the column
        self.constraint: Constraint = constraint  # The constraint of the column

    def cover_column(self):
        """
        'Covers' the column header then loops through all the nodes 
        in the column and covers their rows
        """

        self.left.right = self.right
        self.right.left = self.left

        current = self
        while (current := current.down) != self:
            current.cover_row()

    def uncover_column(self):
        """
        'Uncovers' the rows of all the nodes in this column 
        then 'Uncovers' the column header
        """
        current = self
        while (current := current.up) != self:
            current.uncover_row()

        self.left.right = self
        self.right.left = self
