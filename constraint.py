
class Constraint:
    """Base constraint class used in column header nodes.
    Stores the constraint of the header"""

    def __init__(self) -> None:
        pass


class PositionConstraint(Constraint):
    """Sudoku position constraint"""

    def __init__(self, row, column) -> None:
        self.row = row
        self.column = column


class RowConstraint(Constraint):
    """Sudoku row constraint"""

    def __init__(self, row, number) -> None:
        self.row = row
        self.number = number


class ColumnConstraint(Constraint):
    """Sudoku column constraint"""

    def __init__(self, column, number) -> None:
        self.column = column
        self.number = number


class RegionConstraint(Constraint):
    """Sudoku region constraint"""

    def __init__(self, region, number) -> None:
        self.region = region
        self.number = number
