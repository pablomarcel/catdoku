def is_valid_move(matrix, row, col, number):
    """
    Check if a move is valid in the Sudoku puzzle.
    """
    # Check if the number is already in the row
    for x in range(4):
        if matrix[row][x] == number:
            return False

    # Check if the number is already in the column
    for x in range(4):
        if matrix[x][col] == number:
            return False

    # Check if the number is in the current 2x2 box
    startRow = row - row % 2
    startCol = col - col % 2
    for i in range(2):
        for j in range(2):
            if matrix[i + startRow][j + startCol] == number:
                return False

    return True


def solve_sudoku(matrix):
    """
    Solve a 4x4 Sudoku puzzle using backtracking.
    """
    try:
        empty_found = False
        for i in range(4):
            for j in range(4):
                if matrix[i][j] == 0:
                    row, col = i, j
                    empty_found = True
                    break
            if empty_found:
                break

        if not empty_found:
            return True

        for num in range(1, 5):
            if is_valid_move(matrix, row, col, num):
                matrix[row][col] = num

                if solve_sudoku(matrix):
                    return True

                matrix[row][col] = 0

        return False
    except Exception as e:
        print(f"An error occurred while solving the Sudoku: {e}")
        return False  # Return False or raise the exception depending on how you want to handle it


def solve_and_print_sudoku(puzzle):
    try:
        if solve_sudoku(puzzle):
            for row in puzzle:
                print(" ".join(str(num) for num in row))
        else:
            print("No solution found")
    except Exception as e:
        print(f"An error occurred while printing the Sudoku solution: {e}")


# Example usage
if __name__ == "__main__":
    try:
        puzzle = [[0, 0, 2, 3], [0, 0, 0, 0], [0, 0, 0, 0], [3, 4, 0, 0]]
        print("Sudoku solution:")
        solve_and_print_sudoku(puzzle)
    except Exception as e:
        print(f"An error occurred in the main execution: {e}")
