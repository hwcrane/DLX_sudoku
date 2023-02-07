import numpy as np
import DLXMatrix
import time

def sudoku_solver(sudoku):
    dlx = DLXMatrix.DLX(sudoku)
    result = dlx.search() 
    return result if result is not None else np.array([[-1 for _ in range(9)] for _ in range(9)])

difficulties = ["very_easy", "easy", "medium", "hard"]

times = []
for difficulty in difficulties:
    sudoku = np.load(f"data/{difficulty}_puzzle.npy")
    solutions = np.load(f"data/{difficulty}_solution.npy")

    start = time.time()
    for i in range(15):
        if not (sudoku_solver(sudoku[i]) == solutions[i]).all():
            print(f"Incorrect solution at {difficulty} {i}")
        

    elapsed = (time.time() - start) / 15
    print(f"{difficulty} average time : {(time.time() - start) / 15}s")
