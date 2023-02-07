from typing import Union
from nodes import ColumnConstraint, Constraint, DLXNode, DLXColumn, PositionConstraint, RegionConstraint, RowConstraint
import numpy as np


class DLX:
    def __init__(self, sudoku_grid: np.ndarray) -> None:
        # The head node of the DLX binary matrix
        self.head: DLXColumn = DLXColumn(Constraint())

        # Dictionarys to store refrences to all the column header nodes for the differnt
        # constraint types. They are stored here to speed up creating the binary matrix
        self.position_columns: dict[tuple[int, int], DLXColumn] = {}
        self.row_columns: dict[tuple[int, int], DLXColumn] = {}
        self.column_columns: dict[tuple[int, int], DLXColumn] = {}
        self.region_columns: dict[tuple[int, int], DLXColumn] = {}

        # Create all the column header nodes
        self.create_header_row()

        # Using the passed in sudoku grid, generate a constraints table
        self.create_matrix(sudoku_grid)

        # List to store the temporary soluiton to the exact cover problem
        self.solution: set[DLXNode] = set()

    def create_header_row(self) -> None:
        """Creates all the column header nodes for each constraint"""

        # Add the position constraints
        for row in range(9):
            for column in range(9):
                new_column = DLXColumn(PositionConstraint(row, column))
                self.head.insert_left(new_column)
                self.position_columns[(row, column)] = new_column

        # Add the row constraints
        for row in range(9):
            for number in range(1, 10):
                new_column = DLXColumn(RowConstraint(row, number))
                self.head.insert_left(new_column)
                self.row_columns[(row, number)] = new_column

        # Add the column constraints
        for column in range(9):
            for number in range(1, 10):
                new_column = DLXColumn(ColumnConstraint(column, number))
                self.head.insert_left(new_column)
                self.column_columns[(column, number)] = new_column

        # Add the region constraints
        for region in range(9):
            for number in range(1, 10):
                new_column = DLXColumn(RegionConstraint(region, number))
                self.head.insert_left(new_column)
                self.region_columns[(region, number)] = new_column

    def add_row(self, row: int, column: int, number: int) -> None:
        """Adds a row to the binary matrix"""

        # Calculate which region it is in
        region = (row//3) + 3 * (column//3)

        # Find all the columns where nodes need to be added to using the dictionaries generated
        # when the columns where generated
        columns = [
            self.position_columns[(row, column)],
            self.row_columns[(row, number)],
            self.column_columns[(column, number)],
            self.region_columns[(region, number)],
        ]

        # Step though each column
        prev = None
        for col_node in columns:
            # Create a new node
            new_node = DLXNode(col_node, number)

            # Link it vertically
            col_node.insert_below(new_node)

            # Link it horisontally
            if prev:
                prev.insert_right(new_node)

            prev = new_node

    def create_matrix(self, sudoku_grid: np.ndarray) -> None:
        """Using the `sudoku_grid` numpy array, generates a DLX binary constraint table"""

        # Loop over each square in the grid
        for row in range(9):
            for column in range(9):

                # If there is a 0 in that position, it's value is unknown
                # 9 Rows will need to be added for all the 9 possibilites
                if sudoku_grid[row][column] == 0:

                    # For each of the possibilites for the cell
                    for number in range(1, 10):
                        self.add_row(row, column, number)
                # Else it's value is known and only one row needs to be added
                else:
                    self.add_row(row, column, sudoku_grid[row][column])

    def generate_solution(self) -> np.ndarray:
        solution = np.array([[0] * 9 for _ in range(9)])
        for node in self.solution:
            # Find position constraint
            current = node
            while not isinstance(current.column.constraint, PositionConstraint):
                current = current.right
            solution[current.column.constraint.row][current.column.constraint.column] = node.number
        return solution

    def search(self) -> Union[None,  np.ndarray]:
        """Searches for a soltion to the exact cover problem"""

        # If the matrix is empty, a solution has been found
        if self.head.right == self.head:
            # Generate the solution
            return self.generate_solution()

        # Determine which column to cover
        column = self.get_column_to_search()
        column.cover_column()

        # Loop over all the rows in the column
        row = column
        while (row := row.down) != column:
            # Add row to the temporary solution
            self.solution.add(row)

            # Loop over all the nodes in the row and cover their columns
            node_in_row = row
            while (node_in_row := node_in_row.right) != row:
                node_in_row.column.cover_column()

            # Recursive function call
            solution = self.search()

            # If a solution has been found, return it
            if solution is not None:
                return solution

            # Remove row from the temporary solution
            self.solution.remove(row)

            # Else uncover all the rows that were covered,
            # in the reverse order they were covered
            node_in_row = row
            while (node_in_row := node_in_row.left) != row:
                node_in_row.column.uncover_column()

        # Uncover the column
        column.uncover_column()

    def get_column_to_search(self) -> DLXColumn:
        """Finds the next column to search by finding the column with the smallest size"""

        min_value = self.head.right.size
        min_column = self.head.right
        current = self.head
        while (current := current.right) != self.head:
            if current.size == 0:
                return current
            if current.size < min_value:
                min_value = current.size
                min_column = current
        return min_column
