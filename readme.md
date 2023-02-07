# CM10310 Coursework 1 - Sudoku Solver 

## Initial approach

My initial approach to this problem was to using a backtracking approach. This works by looping over all squares on the sudoku where the value is unknown, then looping over all numbers that square could be. The `check` function then checks that a number possibility is a valid move. If it is, the square is set to that number and the solve function is called recursively. If after checking all number possibilities none are valid, the function returns false and backtracks to try more options. If the number of empty squares is 0, you know the sudoku is solved

Before the sudoku can be solved, the `check_valid` function is used to check that the starting point of the sudoku is a valid sudoku

### The code for the backtracking approach

```py
def check(puzzle: np.ndarray, rowNum: int, columnNum: int, n: int) -> bool:
    # subgrid elment is in
    x, y = (rowNum//3) * 3, (columnNum//3) * 3

    # Check that n does not occur in any of the same row, column, or subgrid
    return np.sum(puzzle[rowNum, :] == n) == 0 \
        and np.sum(puzzle[:, columnNum] == n) == 0 \
        and np.sum(puzzle[x: x+3, y: y+3] == n) == 0


def solve(grid: np.ndarray) -> bool:
    # Get the indexes of the unsolved elements
    rows, columns = np.where(grid == 0)

    # Check if puzzle has been solved
    if len(rows) == 0:
        return True

    # Loop over the unsolved indexes
    for row, col in zip(rows, columns):
        for n in range(1, 10):

            # Check if solution is possible
            if check(grid, row, col, n):

                # Assign element to posible solution
                grid[row, col] = n

                # Reqursive call
                if solve(grid):
                    return True

                # if solution is later shown to be not possible,
                # set element back to 0
                grid[row, col] = 0

        # If none of the solutions were possible, returns false
        return False
    return False


def check_valid(sudoku: np.ndarray) -> bool:
    # Get all the rows and columns with numbers in
    rows, columns = np.where(sudoku != 0)

    # Loop over all those rows
    for row, column in zip(rows, columns):

        # Store the value of the number
        n = sudoku[row][column]

        # Replace that number with a 0
        sudoku[row][column] = 0

        # Check if it would be a valid move to place that number back
        if not check(sudoku, row, column, n):
            # If it is not replace the number then return false as the sudoku is not valid
            sudoku[row][column] = n
            return False

        # Replace the number
        sudoku[row][column] = n
    return True


def solve_backtrack(sudoku: np.ndarray):
    if check_valid(sudoku) and solve(sudoku):
        return sudoku
    return np.array([[-1 for _ in range(9)] for _ in range(9)])
```

## Issue with initial approach 

The backtracking approach worked very fast for the very_easy, easy, and medium sudokus. However it took significant time for the hard ones. This can be seen in the results of a benchmark program I wrote:

| Difficulty   | Average time           | 
|--------------|------------------------|
| very_easy    | 0.0008751222000379736s |
| easy         | 0.0006911277333225978s |
| medium       | 0.0009144972666642085s |
| hard         | 5.62591123893338s      |

## Exact cover problem

After some research, I encountered a way of solving sudokus by reformulating them as exact cover problems. The basics of an exact cover problem is that if you are given a binary matrix, is there a set of rows where there is exactly one 1 in each column. For example for the matrix:

$$
\begin{pmatrix}
0 & 0 & 1 & 0 & 1 & 1 & 0 \\
1 & 0 & 0 & 1 & 0 & 0 & 1 \\
0 & 1 & 1 & 0 & 0 & 1 & 0 \\
1 & 0 & 0 & 1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 & 0 & 0 & 1 \\
0 & 0 & 0 & 1 & 1 & 0 & 1
\end{pmatrix}
$$

The rows are the 1st, 4th, and 5th. Resulting in this matrix

$$
\begin{pmatrix}
0 & 0 & 1 & 0 & 1 & 1 & 0 \\
1 & 0 & 0 & 1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 & 0 & 0 & 1 \\
\end{pmatrix}
$$

This can be used to solve suduko problems by creating a constraint matrix. Where the columns of the matrix represent constraints. There is a then a row for each number in each of the squares. There are four types of constrains:

### Position constraints 

Position constraints insure every square contains one number. There is a position constraint for each of the 81 squares in the sudoku

### Row constraints

Row constraints insure that there is only one of each number. There is a row constraint for each number in each row

### Column constraints

Column constraints are the same as row constraints however are for columns instead of rows

### Region constraints

Region constraints are the same as row and column constraints however are for the regions instead of rows

Each row will have 4 1's in it, one for each constraint. Once the exact cover problem is solved there will be 81 rows, one for each position in the problem.

## Knuths Algorithm X

An efficient method of solving exact cover problems computationally was layed out by Donald E. Knuth in his 2000 paper [Dancing Links](https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/0011047.pdf). 

He explains the method generally as follows:
```
If A is empty, the problem is solved; terminate successfully. Otherwise choose a column, c (deterministically).
Choose a row, r, such that A[r, c] = 1 (nondeterministically). Include r in the partial solution.
For each j such that A[r, j] = 1, 
    delete column j from matrix A; 
    for each i such that A[i, j] = 1,
        delete row i from matrix A.
Repeat this algorithm recursively on the reduced matrix A.
```

Knuth proposes representing the matrix using doubly linked circular lists. Where the 1's in the matrix are node objects with pointers pointing to the nodes up, down, left, right, and the column node. Each column is then also a node. Here is what this would look like:

He suggests this firstly because the constraint matrix is inherently sparse, and also it allows for rows and columns to be quickly hidden and uncovered by modifying the pointers. He calls this method dancing links.

The pseudocode for this dancing links approach is as follows;
```
If R[h] = h, print the current solution and return. 
Otherwise choose a column object c.
Cover column c.
For each r ← D[c], D[D[c]], ..., while r != c,
    set O_k ← r;
    for each j ← R[r], R[R[r]], ..., while j != r,
        cover column j; 
    search(k + 1);
    set r ← O_k and c ← C[r];
    for each j ← L[r], L[L[r]], ..., while j != r,
        uncover column j. 
Uncover column c and return
```

## New approach

My new approach therefore formulated the sudoku as an exact cover problem and solved it using Knuths dancing links technique. The nodes of the binary matrix are the class `DLXNode`. Column node are `DLXColumn` which inherit from `DLXNode` however have extra attributes for the column constraint and methods to cover and uncover the column. The constraints for the column nodes are stored in a `Constraint` class which separate classes for position, row, column, and region constraints inherit from.

The class `DLXMatrix` constructs the binary matrix using a provided sudoku problem. When constructing, if the value of a square is know, 1 row is added to the matrix for the known number. If it is not 9 rows are added for each possible number

The `search` method finds the solution to the exact cover problem and is based on the pseudocode in Knuths paper. Once a solution is found, the method `generate_solution` creates the sudoku solution. If no solution is found the method returns `None`

## Speed comparison

Here is a comparison of the backtracking and dancing links implementations:

| Difficulty   | Backtracking Av. Time  | Dancing Links Av. Time |
|--------------|------------------------|------------------------|
| very_easy    | 0.0008751222000379736s | 0.001321316666629476s  |
| easy         | 0.0006911277333225978s | 0.000992341666521194s  |
| medium       | 0.0009144972666642085s | 0.004131138866553859s  |
| hard         | 5.62591123893338s      | 0.0020641333336243405s |

As you can see the dancing links approach solves the hard Sudoku's 2800 times faster. However it is slower for the very_easy, easy, and medium difficulty sudokus. I believe this is due to the time taken to construct the constraint matrix. 
