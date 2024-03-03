import random


def is_valid_move(puzzle, row, col, number):
    # Check if the number is already in the given row
    for x in range(4):
        if puzzle[row][x] == number:
            return False

    # Check if the number is already in the given column
    for x in range(4):
        if puzzle[x][col] == number:
            return False

    # Check if the number is already in the 2x2 grid
    start_row = row - row % 2
    start_col = col - col % 2
    for i in range(2):
        for j in range(2):
            if puzzle[start_row + i][start_col + j] == number:
                return False

    return True


def find_empty_location(puzzle):
    for i in range(4):
        for j in range(4):
            if puzzle[i][j] == 0:
                return (i, j)
    return None


def generate_puzzle():
    puzzle = [[0 for _ in range(4)] for _ in range(4)]
    if fill_puzzle(puzzle):
        return puzzle
    else:
        raise Exception("Failed to generate a valid puzzle")


def fill_puzzle(puzzle):
    empty_location = find_empty_location(puzzle)
    if not empty_location:
        return True  # Puzzle is complete
    row, col = empty_location

    numbers = list(range(1, 5))
    random.shuffle(numbers)  # Randomize the order of numbers
    for number in numbers:
        if is_valid_move(puzzle, row, col, number):
            puzzle[row][col] = number
            if fill_puzzle(puzzle):
                return True
            puzzle[row][col] = 0  # Undo and try again
    return False


if __name__ == "__main__":
    puzzle = generate_puzzle()
    for row in puzzle:
        print(row)
