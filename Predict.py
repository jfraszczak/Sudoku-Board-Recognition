from keras.models import load_model
import numpy as np
import Digits
import Sudoku


def predict(grid, grid_info):
    model = load_model('my_model1.h5')

    final_grid = []
    index = 0
    for i in range(len(grid_info)):
        if grid_info[i] == 1:
            prediction = model.predict(np.array([grid[index]]))
            final_grid.append(read_label(prediction))
            index += 1
        else:
            final_grid.append('BLANK')
    return final_grid

def read_label(prediction):
    max = 0
    label = 0
    for i in range(10):
        if prediction[0][i] > max:
            max = prediction[0][i]
            label = i
    return label

def show_grid(grid):
    print("-" * 25)
    for i in range(9):
        print(("|" + " {} {} {} |" * 3).format(*[grid[9 * i + j] if grid[9 * i + j] != 'BLANK' else "." for j in range(9)]))
        if i == 8:
            print("-" * 25)
        elif i % 3 == 2:
            print("|" + "-" * 23 + "|")
    print('\n')

def main(file, show):
    digits = Sudoku.main(file, show)
    grid, grid_info = Digits.read_grid(digits)
    grid = predict(grid, grid_info)
    show_grid(grid)

    return grid
