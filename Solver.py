from copy import copy, deepcopy
import Predict
import pygame

def draw(screen, size, matrix):
    for i in range(9 + 1):
        if i % 3 == 0:
            w = 4
        else:
            w = 2
        pygame.draw.lines(screen, (0 ,0 ,0), True, [(0, size / 9 * i), (size, size / 9 * i)], w)
        pygame.draw.lines(screen, (0 ,0 ,0), True, [(size / 9 * i, 0), (size / 9 * i, size)], w)


        for i in range(9):
            for j in range(9):
                text = ''
                if matrix[i][j][1] == 0:
                    for digit in matrix[i][j][0]:
                        text += str(digit)

                    x = j * size / 9 + 0.005 * size
                    y = i * size / 9 + 0.005 * size
                    font = pygame.font.SysFont('Arial', 16)
                    text = font.render(text, True, (0, 0, 255))
                    screen.blit(text, (x, y))

                else:
                    text = str(matrix[i][j][0][0])
                    x = j * size / 9 + 0.045 * size
                    y = i * size / 9 + 0.02 * size
                    font = pygame.font.SysFont('Arial', 40)
                    text = font.render(text, True, (0, 0, 0))
                    screen.blit(text, (x, y))

class Sudoku:
    def __init__(self, grid, show_steps):
        self.changes = []
        self.matrix = []
        self.recursion_executions = 0
        self.steps = show_steps
        self.step_counter = 1
        self.hidden_singles_flag = False
        row = 0
        for i in range(9):
            pom = []
            column = 0
            for j in range(9):
                if grid[i * 9 + j] == 'BLANK':
                    pom.append([[1, 2, 3, 4, 5, 6, 7, 8, 9], 0])
                else:
                    pom.append([[grid[i * 9 + j]], 1])
                    self.changes.append([row, column])
                column += 1
            row += 1
            self.matrix.append(pom)
        self.update()

    def rows_update(self):
        flag = False
        for coordinates in self.changes:
            number = self.matrix[coordinates[0]][coordinates[1]][0][0]
            for i in range(9):
                if self.matrix[coordinates[0]][i][1] == 0:
                    if number in self.matrix[coordinates[0]][i][0]:
                        self.matrix[coordinates[0]][i][0].remove(number)
                        if self.steps:
                            print(("{}. UPDATE POTENTIAL SOLUTIONS - DELETE POTENTIAL DIGIT {} FROM [{}, {}] -- ROW").format(self.step_counter, number, coordinates[0] + 1, i + 1))
                            self.step_counter += 1
                        flag = True
        return flag

    def columns_update(self):
        flag = False
        for coordinates in self.changes:
            number = self.matrix[coordinates[0]][coordinates[1]][0][0]
            for i in range(9):
                if self.matrix[i][coordinates[1]][1] == 0:
                    if number in self.matrix[i][coordinates[1]][0]:
                        self.matrix[i][coordinates[1]][0].remove(number)
                        if self.steps:
                            print(("{}. UPDATE POTENTIAL SOLUTIONS - DELETE POTENTIAL DIGIT {} FROM [{}, {}] -- COLUMN").format(self.step_counter, number, i + 1, coordinates[1] + 1))
                            self.step_counter += 1
                            flag = True
        return flag

    def which_sector(self, coordinates):
        if coordinates[0] >= 0 and coordinates[0] <= 2:
            row = 0
        elif coordinates[0] >= 3 and coordinates[0] <= 5:
            row = 1
        elif coordinates[0] >= 6 and coordinates[0] <= 8:
            row = 2

        if coordinates[1] >= 0 and coordinates[1] <= 2:
            column = 0
        elif coordinates[1] >= 3 and coordinates[1] <= 5:
            column = 1
        elif coordinates[1] >= 6 and coordinates[1] <= 8:
            column = 2
        return [row, column]

    def sector_update(self):
        flag = False
        rng = [[0, 3], [3, 6], [6, 9]]
        for coordinates in self.changes:
            number = self.matrix[coordinates[0]][coordinates[1]][0][0]
            sector = self.which_sector(coordinates)
            rangeX = rng[sector[0]]
            rangeY = rng[sector[1]]
            for x in range(rangeX[0], rangeX[1]):
                for y in range(rangeY[0], rangeY[1]):
                    if self.matrix[x][y][1] == 0:
                        if number in self.matrix[x][y][0]:
                            self.matrix[x][y][0].remove(number)
                            if self.steps:
                                print(("{}. UPDATE POTENTIAL SOLUTIONS - DELETE POTENTIAL DIGIT {} FROM [{}, {}] -- SECTOR").format(self.step_counter, number, x + 1, y + 1))
                                self.step_counter += 1
                            flag = True
        return flag

    def update(self):
        self.rows_update()
        self.columns_update()
        self.sector_update()

    def single_possible_digit_rows(self):
        i = 0
        flag = False
        while i < 9:
            self.changes = []
            digits = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            for j in range(9):
                if self.matrix[i][j][1] == 0:
                    for k in range(len(self.matrix[i][j][0])):
                        digits[self.matrix[i][j][0][k] - 1] += 1
            for n in range(len(digits)):
                if digits[n] == 1:
                    for j in range(9):
                        if n + 1 in self.matrix[i][j][0]:
                            self.matrix[i][j][0] = [n + 1]
                            self.matrix[i][j][1] = 1
                            self.changes.append([i, j])
                            if self.steps:
                               print(("{}. HIDDEN SINGLES - SET {} IN [{}, {}] -- ROW").format(self.step_counter, n + 1, i + 1, j + 1))
                               self.step_counter += 1
                            flag = True
            if len(self.changes) > 0:
                self.update()
                if self.steps:
                    self.show_sudoku_grid()
                i = 0
            else:
                i += 1
        return flag

    def single_possible_digit_columns(self):
        i = 0
        flag = False
        while i < 9:
            self.changes = []
            digits = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            for j in range(9):
                if self.matrix[j][i][1] == 0:
                    for k in range(len(self.matrix[j][i][0])):
                        digits[self.matrix[j][i][0][k] - 1] += 1
            for n in range(len(digits)):
                if digits[n] == 1:
                    for j in range(9):
                        if n + 1 in self.matrix[j][i][0]:
                            self.matrix[j][i][0] = [n + 1]
                            self.matrix[j][i][1] = 1
                            self.changes.append([j, i])
                            if self.steps:
                                print(("{}. HIDDEN SINGLES - SET {} IN [{}, {}] -- COLUMN").format(self.step_counter, n + 1, j + 1, i + 1))
                                self.step_counter += 1
                            flag = True
            if len(self.changes) > 0:
                self.update()
                if self.steps:
                    self.show_sudoku_grid()
                self.single_possible_digit_rows()
                i = 0
            else:
                i += 1
        return flag

    def single_possible_digit_sectors(self):
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        i = 0
        j = 0
        flag = False
        while i < 3:
            while j < 3:
                self.changes = []
                digits = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                for x in rng[i]:
                    for y in rng[j]:
                        if self.matrix[x][y][1] == 0:
                            for k in range(len(self.matrix[x][y][0])):
                                digits[self.matrix[x][y][0][k] - 1] += 1
                for n in range(len(digits)):
                    if digits[n] == 1:
                        for x in rng[i]:
                            for y in rng[j]:
                                if n + 1 in self.matrix[x][y][0]:
                                    self.matrix[x][y][0] = [n + 1]
                                    self.matrix[x][y][1] = 1
                                    self.changes.append([x, y])
                                    if self.steps:
                                        print(("{}. HIDDEN SINGLES - SET {} IN [{}, {}] -- SECTOR").format(self.step_counter, n + 1, x + 1, y + 1))
                                        self.step_counter += 1
                                    flag = True
                if len(self.changes) > 0:
                    self.update()
                    if self.steps:
                        self.show_sudoku_grid()
                    self.single_possible_digit_rows()
                    self.single_possible_digit_columns()
                    j = 0
                else:
                    j += 1
            if len(self.changes) > 0:
                i = 0
            else:
                i += 1
        return flag

    def single_possible_digits(self):
        flag1 = self.single_possible_digit_rows()
        flag2 = self.single_possible_digit_columns()
        flag3 = self.single_possible_digit_sectors()
        return flag1 or flag2 or flag3

    def locked_candidates_type1_rows_single_sector(self, i , j):
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        flag = False
        for row in rng[i]:
            for digit in self.matrix[row][rng[j][0]][0]:
                condition = 0
                if digit in self.matrix[row][rng[j][1]][0] or digit in self.matrix[row][rng[j][2]][0]:
                    for k in range(3):
                        if k != row % 3:
                            if digit not in self.matrix[rng[i][k]][rng[j][0]][0] and digit not in self.matrix[rng[i][k]][rng[j][1]][0] and digit not in self.matrix[rng[i][k]][rng[j][2]][0]:
                                condition += 1
                if condition == 2:
                    for k in range(3):
                        if k != j:
                            for column in rng[k]:
                                if digit in self.matrix[row][column][0]:
                                    self.matrix[row][column][0].remove(digit)
                                    if self.steps:
                                        print(("{}. LOCKED CANDIDATES TYPE 1 - DELETE {} FROM [{}, {}] -- ROW").format(self.step_counter, digit, row + 1, column + 1, i + 1, j + 1))
                                        self.step_counter += 1
                                    flag = True
            for digit in self.matrix[row][rng[j][1]][0]:
                condition = 0
                if digit in self.matrix[row][rng[j][2]][0]:
                    for k in range(3):
                        if k != row % 3:
                            if digit not in self.matrix[rng[i][k]][rng[j][0]][0] and digit not in self.matrix[rng[i][k]][rng[j][1]][0] and digit not in self.matrix[rng[i][k]][rng[j][2]][0]:
                                condition += 1
                if condition == 2:
                    for k in range(3):
                        if k != j:
                            for column in rng[k]:
                                if digit in self.matrix[row][column][0]:
                                    self.matrix[row][column][0].remove(digit)
                                    if self.steps:
                                        print(("{}. LOCKED CANDIDATES TYPE 1 - DELETE {} FROM [{}, {}] -- ROW").format(self.step_counter, digit, row + 1, column + 1, row + 1, i + 1, j + 1))
                                        self.step_counter += 1
                                    flag = True
        return flag

    def locked_candidates_type1_rows(self):
        flag = False
        i = 0
        while i < 3:
            j = 0
            while j < 3:
                condition = self.locked_candidates_type1_rows_single_sector(i, j)
                flag = flag or condition
                if condition:
                    if j > 0:
                        j = 0
                else:
                    j += 1
            i += 1
        return flag

    def locked_candidates_type1_columns_single_sector(self, i , j):
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        flag = False
        for column in rng[j]:
            for digit in self.matrix[rng[i][0]][column][0]:
                condition = 0
                if digit in self.matrix[rng[i][1]][column][0] or digit in self.matrix[rng[i][2]][column][0]:
                    for k in range(3):
                        if k != column % 3:
                            if digit not in self.matrix[rng[i][0]][rng[j][k]][0] and digit not in self.matrix[rng[i][1]][rng[j][k]][0] and digit not in self.matrix[rng[i][2]][rng[j][k]][0]:
                                condition += 1
                if condition == 2:
                    for k in range(3):
                        if k != i:
                            for row in rng[k]:
                                if digit in self.matrix[row][column][0]:
                                    self.matrix[row][column][0].remove(digit)
                                    if self.steps:
                                        print(("{}. LOCKED CANDIDATES TYPE 1 - DELETE {} FROM [{}, {}] -- COLUMN").format(self.step_counter, digit, row + 1, column + 1, row + 1, i + 1, j + 1))
                                        self.step_counter += 1
                                    flag = True
            for digit in self.matrix[rng[i][1]][column][0]:
                condition = 0
                if digit in self.matrix[rng[i][2]][column][0]:
                    for k in range(3):
                        if k != column % 3:
                            if digit not in self.matrix[rng[i][0]][rng[j][k]][0] and digit not in self.matrix[rng[i][1]][rng[j][k]][0] and digit not in self.matrix[rng[i][2]][rng[j][k]][0]:
                                condition += 1
                if condition == 2:
                    for k in range(3):
                        if k != i:
                            for row in rng[k]:
                                if digit in self.matrix[row][column][0]:
                                    self.matrix[row][column][0].remove(digit)
                                    if self.steps:
                                        print(("{}. LOCKED CANDIDATES TYPE 1 - DELETE {} FROM [{}, {}] -- COLUMN").format(self.step_counter, digit, row + 1, column + 1, row + 1, i + 1, j + 1))
                                        self.step_counter += 1
                                    flag = True
        return flag

    def locked_candidates_type1_columns(self):
        flag = False
        i = 0
        while i < 3:
            j = 0
            while j < 3:
                condition = self.locked_candidates_type1_columns_single_sector(j, i)
                flag = flag or condition
                if condition:
                    if j > 0:
                        j = 0
                else:
                    j += 1
            i += 1
        return flag

    def locked_candidates_type1(self):
        condition = True
        flag = False
        while condition:
            flag = flag or self.locked_candidates_type1_rows()
            condition = self.locked_candidates_type1_columns()
            flag = flag or condition
        return flag

    def locked_candidates_type2_single_row(self, row):
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        flag = False
        for i in range(3):
            if self.matrix[row][rng[i][0]][1] == 0:
                for digit in self.matrix[row][rng[i][0]][0]:
                    condition = 0
                    if digit in self.matrix[row][rng[i][1]][0] or digit in self.matrix[row][rng[i][2]][0]:
                        for j in range(3):
                            if j != i:
                                for column in rng[j]:
                                    if digit not in self.matrix[row][column][0]:
                                        condition += 1
                    if condition == 6:
                        if row <= 2:
                            sector = 0
                        elif row <= 5:
                            sector = 1
                        else:
                            sector = 2
                        for j in rng[sector]:
                            if j != row:
                                for column in rng[i]:
                                    if digit in self.matrix[j][column][0]:
                                        self.matrix[j][column][0].remove(digit)
                                        if self.steps:
                                            print(("{}. LOCKED CANDIDATES TYPE 2 - DELETE {} FROM [{}, {}] -- ROW").format(self.step_counter, digit, j + 1, column + 1))
                                            self.step_counter += 1
                                        flag = True
            if self.matrix[row][rng[i][1]][1] == 0:
                for digit in self.matrix[row][rng[i][1]][0]:
                    condition = 0
                    if digit in self.matrix[row][rng[i][2]][0]:
                        for j in range(3):
                            if j != i:
                                for column in rng[j]:
                                    if digit not in self.matrix[row][column][0]:
                                        condition += 1
                    if condition == 6:
                        if row <= 2:
                            sector = 0
                        elif row <= 5:
                            sector = 1
                        else:
                            sector = 2
                        for j in rng[sector]:
                            if j != row:
                                for column in rng[i]:
                                    if digit in self.matrix[j][column][0]:
                                        self.matrix[j][column][0].remove(digit)
                                        if self.steps:
                                            print(("{}. LOCKED CANDIDATES TYPE 2 - DELETE {} FROM [{}, {}] -- ROW").format(self.step_counter, digit, j + 1, column + 1))
                                            self.step_counter += 1
                                        flag = True
        return flag

    def locked_candidates_type2_rows(self):
        row = 0
        flag = False
        while row < 9:
            condition = self.locked_candidates_type2_single_row(row)
            flag = flag or condition
            if condition and row > 0:
                row = 0
            else:
                row += 1
        return flag

    def locked_candidates_type2_single_column(self, column):
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        flag = False
        for i in range(3):
            if self.matrix[rng[i][0]][column][1] == 0:
                for digit in self.matrix[rng[i][0]][column][0]:
                    condition = 0
                    if digit in self.matrix[rng[i][1]][column][0] or digit in self.matrix[rng[i][2]][column][0]:
                        for j in range(3):
                            if j != i:
                                for row in rng[j]:
                                    if digit not in self.matrix[row][column][0]:
                                        condition += 1
                    if condition == 6:
                        if column <= 2:
                            sector = 0
                        elif column <= 5:
                            sector = 1
                        else:
                            sector = 2
                        for j in rng[sector]:
                            if j != column:
                                for row in rng[i]:
                                    if digit in self.matrix[row][j][0]:
                                        self.matrix[row][j][0].remove(digit)
                                        if self.steps:
                                            print(("{}. LOCKED CANDIDATES TYPE 2 - DELETE {} FROM [{}, {}] -- COLUMN").format(self.step_counter, digit, row + 1, j + 1))
                                            self.step_counter += 1
                                        flag = True
            if self.matrix[rng[i][1]][column][1] == 0:
                for digit in self.matrix[rng[i][1]][column][0]:
                    condition = 0
                    if digit in self.matrix[rng[i][2]][column][0]:
                        for j in range(3):
                            if j != i:
                                for row in rng[j]:
                                    if digit not in self.matrix[row][column][0]:
                                        condition += 1
                    if condition == 6:
                        if column <= 2:
                            sector = 0
                        elif column <= 5:
                            sector = 1
                        else:
                            sector = 2
                        for j in rng[sector]:
                            if j != column:
                                for row in rng[i]:
                                    if digit in self.matrix[row][j][0]:
                                        self.matrix[row][j][0].remove(digit)
                                        if self.steps:
                                            print(("{}. LOCKED CANDIDATES TYPE 2 - DELETE {} FROM [{}, {}] -- COLUMN").format(self.step_counter, digit, row + 1, j + 1))
                                            self.step_counter += 1
                                        flag = True
        return flag

    def locked_candidates_type2_columns(self):
        column = 0
        flag = False
        while column < 9:
            condition = self.locked_candidates_type2_single_column(column)
            flag = flag or condition
            if condition and column > 0:
                column = 0
            else:
                column += 1
        return flag

    def locked_candidates_type2(self):
        condition = True
        flag = False
        while condition:
            flag = flag or self.locked_candidates_type2_rows()
            condition = self.locked_candidates_type2_columns()
            flag = flag or condition
        return flag

    def compare(self, a, b):
        flag = True
        for i in range(len(a)):
            flag = flag and (a[i] == b[i])
        return flag

    def naked_pairs_rows(self):
        flag = False
        for row in range(9):
            for i in range(9):
                for j in range(9):
                    if len(self.matrix[row][i][0]) == len(self.matrix[row][j][0]) and len(self.matrix[row][i][0]) == 2 and i != j:
                        if self.compare(self.matrix[row][i][0], self.matrix[row][j][0]):
                            for digit in self.matrix[row][i][0]:
                                for column in range(9):
                                    if digit in self.matrix[row][column][0] and column != i and column != j:
                                        self.matrix[row][column][0].remove(digit)
                                        if self.steps:
                                            print(('{}. NAKED PAIRS - DELETE {} FROM [{}, {}] -- ROW').format(self.step_counter, digit, row + 1, column + 1))
                                        flag = True
        return flag

    def naked_pairs_columns(self):
        flag = False
        for column in range(9):
            for i in range(9):
                for j in range(9):
                    if len(self.matrix[i][column][0]) == len(self.matrix[j][column][0]) and len(self.matrix[i][column][0]) == 2 and i != j:
                        if self.compare(self.matrix[i][column][0], self.matrix[j][column][0]):
                            for digit in self.matrix[i][column][0]:
                                for row in range(9):
                                    if digit in self.matrix[row][column][0] and i != row and j != row:
                                        self.matrix[row][column][0].remove(digit)
                                        if self.steps:
                                            print(('{}. NAKED PAIRS - DELETE {} FROM [{}, {}] -- COLUMN').format(self.step_counter, digit, row + 1,column + 1))
                                        flag = True
        return flag

    def naked_pairs_sectors(self):
        flag = False
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        for sector in range(9):
            for i in range(9):
                for j in range(9):
                    if (len(self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0]) == len(self.matrix[rng[int(sector / 3)][int(j / 3)]][rng[sector % 3][j % 3]][0])
                        and len(self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0]) == 2 and i != j):
                        if self.compare(self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0], self.matrix[rng[int(sector / 3)][int(j / 3)]][rng[sector % 3][j % 3]][0]):
                            for digit in self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0]:
                                for box in range(9):
                                    if digit in self.matrix[rng[int(sector / 3)][int(box / 3)]][rng[sector % 3][box % 3]][0] and i != box and j != box:
                                        self.matrix[rng[int(sector / 3)][int(box / 3)]][rng[sector % 3][box % 3]][0].remove(digit)
                                        if self.steps:
                                            print(('{}. NAKED PAIRS - DELETE {} FROM [{}, {}] -- SECTOR').format(self.step_counter, digit, rng[int(sector / 3)][int(box / 3)] + 1, rng[sector % 3][box % 3] + 1))
                                        flag = True
        return flag

    def naked_pairs(self):
        flag = False
        flag1 = True
        while flag1:
            flag2 = True
            while flag2:
                flag3 = self.naked_pairs_rows()
                flag2 = self.naked_pairs_columns()
                flag = flag or flag2 or flag3
            flag1 = self.naked_pairs_sectors()
            flag = flag or flag1
        return flag

    def unique_elements(self, a, b, c):
        unique = []
        for array in [a, b, c]:
            for element in array:
                if element not in unique:
                    unique.append(element)
        return (len(unique) == 3)

    def compare_naked_triples(self, a, b, c):
        flag = False
        if len(a) > 1 and len(a) <= 3 and len(b) > 1 and len(b) <= 3 and len(c) > 1 and len(c) <= 3:
            if self.unique_elements(a, b, c):
                flag = True
        return flag

    def naked_triples_rows(self):
        flag = False
        for row in range(9):
            for i in range(9):
                for j in range(9):
                    for k in range(9):
                        if self.compare_naked_triples(self.matrix[row][i][0], self.matrix[row][j][0], self.matrix[row][k][0]) and i != j and i != k and j != k:
                            for array in [self.matrix[row][i][0], self.matrix[row][j][0], self.matrix[row][k][0]]:
                                for digit in array:
                                    for column in range(9):
                                        if digit in self.matrix[row][column][0] and column != i and column != j and column != k:
                                            self.matrix[row][column][0].remove(digit)
                                            if self.steps:
                                                print(('{}. NAKED TRIPLES - DELETE {} FROM [{}, {}] -- ROW').format(self.step_counter, digit, row + 1, column + 1))
                                            flag = True
        return flag

    def naked_triples_columns(self):
        flag = False
        for column in range(9):
            for i in range(9):
                for j in range(9):
                    for k in range(9):
                        if self.compare_naked_triples(self.matrix[i][column][0], self.matrix[j][column][0], self.matrix[k][column][0]) and i != j and i != k and j != k:
                            for array in [self.matrix[i][column][0], self.matrix[j][column][0], self.matrix[k][column][0]]:
                                for digit in array:
                                    for row in range(9):
                                        if digit in self.matrix[row][column][0] and row != i and row != j and row != k:
                                            self.matrix[row][column][0].remove(digit)
                                            if self.steps:
                                                print(('{}. NAKED TRIPLES - DELETE {} FROM [{}, {}] -- COLUMN').format(self.step_counter, digit, row + 1, column + 1))
                                            flag = True
        return flag

    def naked_triples_sectors(self):
        flag = False
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        for sector in range(9):
            for i in range(9):
                for j in range(9):
                    for k in range(3):
                        if (self.compare_naked_triples(self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0], self.matrix[rng[int(sector / 3)][int(j / 3)]][rng[sector % 3][j % 3]][0], self.matrix[rng[int(sector / 3)][int(k / 3)]][rng[sector % 3][k % 3]][0])
                            and i != j and i != k and j != k):
                            for array in [self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0], self.matrix[rng[int(sector / 3)][int(j / 3)]][rng[sector % 3][j % 3]][0], self.matrix[rng[int(sector / 3)][int(k / 3)]][rng[sector % 3][k % 3]][0]]:
                                for digit in array:
                                    for box in range(9):
                                        if digit in self.matrix[rng[int(sector / 3)][int(box / 3)]][rng[sector % 3][box % 3]][0] and i != box and j != box and k != box:
                                            self.matrix[rng[int(sector / 3)][int(box / 3)]][rng[sector % 3][box % 3]][0].remove(digit)
                                            if self.steps:
                                                print(('{}. NAKED TRIPLES - DELETE {} FROM [{}, {}] -- SECTOR').format(self.step_counter, digit, rng[int(sector / 3)][int(box / 3)] + 1, rng[sector % 3][box % 3] + 1))
                                            flag = True
        return flag

    def naked_triples(self):
        flag = False
        flag1 = True
        while flag1:
            flag2 = True
            while flag2:
                flag3 = self.naked_triples_rows()
                flag2 = self.naked_triples_columns()
                flag = flag or flag2 or flag3
            flag1 = self.naked_triples_sectors()
            flag = flag or flag1
        return flag

    def hidden_pairs_rows(self):
        flag = False
        for row in range(9):
            for index in range(9):
                for digit1 in self.matrix[row][index][0]:
                    for digit2 in self.matrix[row][index][0]:
                        if digit1 != digit2:
                            pair = 1
                            none = 0
                            for i in range(9):
                                if i != index:
                                    if digit1 in self.matrix[row][i][0] and digit2 in self.matrix[row][i][0]:
                                        pair += 1
                                        index2 = i
                                    if digit1 not in self.matrix[row][i][0] and digit2 not in self.matrix[row][i][0]:
                                        none += 1
                            if pair == 2 and none == 7:
                                for i in [index, index2]:
                                    digit = 0
                                    while digit < len(self.matrix[row][i][0]):
                                        if self.matrix[row][i][0][digit] != digit1 and self.matrix[row][i][0][digit] != digit2:
                                            if self.steps:
                                                print(("{}. HIDDEN PAIRS - DELETE {} FROM [{}, {}] -- ROW").format(self.step_counter, self.matrix[row][i][0][digit], row + 1, i + 1))
                                                self.step_counter += 1
                                            self.matrix[row][i][0].remove(self.matrix[row][i][0][digit])
                                            flag = True
                                            digit -= 1
                                        digit += 1
        return flag

    def hidden_pairs_columns(self):
        flag = False
        for column in range(9):
            for index in range(9):
                for digit1 in self.matrix[index][column][0]:
                    for digit2 in self.matrix[index][column][0]:
                        if digit1 != digit2:
                            pair = 1
                            none = 0
                            for i in range(9):
                                if i != index:
                                    if digit1 in self.matrix[i][column][0] and digit2 in self.matrix[i][column][0]:
                                        pair += 1
                                        index2 = i
                                    if digit1 not in self.matrix[i][column][0] and digit2 not in self.matrix[i][column][0]:
                                        none += 1
                            if pair == 2 and none == 7:
                                for i in [index, index2]:
                                    digit = 0
                                    while digit < len(self.matrix[i][column][0]):
                                        if self.matrix[i][column][0][digit] != digit1 and self.matrix[i][column][0][digit] != digit2:
                                            if self.steps:
                                                print(("{}. HIDDEN PAIRS - DELETE {} FROM [{}, {}] -- COLUMN").format(self.step_counter, self.matrix[i][column][0][digit], i + 1, column + 1))
                                                self.step_counter += 1
                                            self.matrix[i][column][0].remove(self.matrix[i][column][0][digit])
                                            flag = True
                                            digit -= 1
                                        digit += 1
        return flag

    def hidden_pairs_sectors(self):
        flag = False
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        for sector in range(9):
            for index in range(9):
                for digit1 in self.matrix[rng[int(sector / 3)][int(index / 3)]][rng[sector % 3][index % 3]][0]:
                    for digit2 in self.matrix[rng[int(sector / 3)][int(index / 3)]][rng[sector % 3][index % 3]][0]:
                        if digit1 != digit2:
                            pair = 1
                            none = 0
                            for i in range(9):
                                if i != index:
                                    if digit1 in self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0] and digit2 in self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0]:
                                        pair += 1
                                        index2 = i
                                    if digit1 not in self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0] and digit2 not in self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0]:
                                        none += 1
                            if pair == 2 and none == 7:
                                for i in [index, index2]:
                                    digit = 0
                                    while digit < len(self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0]):
                                        if self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0][digit] != digit1 and self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0][digit] != digit2:
                                            if self.steps:
                                                print(("{}. HIDDEN PAIRS - DELETE {} FROM [{}, {}] -- SECTOR").format(self.step_counter, self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0][digit], rng[int(sector / 3)][int(i / 3)] + 1, rng[sector % 3][i % 3] + 1))
                                                self.step_counter += 1
                                            self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0].remove(self.matrix[rng[int(sector / 3)][int(i / 3)]][rng[sector % 3][i % 3]][0][digit])
                                            flag = True
                                            digit -= 1
                                        digit += 1
        return flag

    def hidden_pairs(self):
        flag = False
        flag1 = True
        while flag1:
            flag2 = True
            while flag2:
                flag3 = self.hidden_pairs_rows()
                flag2 = self.hidden_pairs_columns()
                flag = flag or flag2 or flag3
            flag1 = self.hidden_pairs_sectors()
            flag = flag or flag1
        return flag

    def triple_containing(self, array, elements):
        k = 0
        for element in elements:
            if element in array:
                k += 1
        return (k == 2 or k == 3)

    def triple_not_containing(self, array, elements):
        k = 0
        for element in elements:
            if element not in array:
                k += 1
        return (k == 3)

    def delete_from_matrix_rows(self, row, columns, elements):
        flag = False
        for column in columns:
            i = 0
            while i < len(self.matrix[row][column][0]):
                if self.matrix[row][column][0][i] not in elements:
                    if self.steps:
                        print(('{}. HIDDEN TRIPLES - DELETE {} FROM [{}, {}] -- ROW').format(self.step_counter, self.matrix[row][column][0][i], row + 1, column + 1))
                        print(elements)
                        self.step_counter += 1
                    self.matrix[row][column][0].remove(self.matrix[row][column][0][i])
                    flag = True
                    i -= 1
                i += 1
        return flag

    def hidden_triples_rows(self):
        flag = False
        for row in range(9):
            for i in range(1, 10):
                for j in range(i + 1, 10):
                    for k in range(j + 1, 10):
                        triples = 0
                        none = 0
                        columns = []
                        for column in range(9):
                            if self.triple_containing(self.matrix[row][column][0], [i, j, k]):
                                triples += 1
                                columns.append(column)
                            elif self.triple_not_containing(self.matrix[row][column][0], [i, j, k]):
                                none += 1
                        if triples == 3 and none == 6:
                            flag = flag or self.delete_from_matrix_rows(row, columns, [i, j, k])
        return flag

    def delete_from_matrix_columns(self, rows, column, elements):
        flag = False
        for row in rows:
            i = 0
            while i < len(self.matrix[row][column][0]):
                if self.matrix[row][column][0][i] not in elements:
                    if self.steps:
                        print(('{}. HIDDEN TRIPLES - DELETE {} FROM [{}, {}] -- COLUMN').format(self.step_counter, self.matrix[row][column][0][i], row + 1, column + 1))
                        print(elements)
                        self.step_counter += 1
                    self.matrix[row][column][0].remove(self.matrix[row][column][0][i])
                    flag = True
                    i -= 1
                i += 1
        return flag

    def hidden_triples_columns(self):
        flag = False
        for column in range(9):
            for i in range(1, 10):
                for j in range(i + 1, 10):
                    for k in range(j + 1, 10):
                        triples = 0
                        none = 0
                        rows = []
                        for row in range(9):
                            if self.triple_containing(self.matrix[row][column][0], [i, j, k]):
                                triples += 1
                                rows.append(row)
                            elif self.triple_not_containing(self.matrix[row][column][0], [i, j, k]):
                                none += 1
                        if triples == 3 and none == 6:
                            flag = flag or self.delete_from_matrix_columns(rows, column, [i, j, k])
        return flag

    def delete_from_matrix_sectors(self, sector, boxes, elements):
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        flag = False
        for box in boxes:
            row = rng[int(sector / 3)][int(box / 3)]
            column = rng[sector % 3][box % 3]
            i = 0
            while i < len(self.matrix[row][column][0]):
                if self.matrix[row][column][0][i] not in elements:
                    if self.steps:
                        print(('{}. HIDDEN TRIPLES - DELETE {} FROM [{}, {}] -- SECTOR').format(self.step_counter, self.matrix[row][column][0][i], row + 1, column + 1))
                        print(elements)
                        self.step_counter += 1
                    self.matrix[row][column][0].remove(self.matrix[row][column][0][i])
                    flag = True
                    i -= 1
                i += 1
        return flag

    def hidden_triples_sectors(self):
        flag = False
        rng = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        for sector in range(9):
            for i in range(1, 10):
                for j in range(i + 1, 10):
                    for k in range(j + 1, 10):
                        triples = 0
                        none = 0
                        boxes = []
                        for box in range(9):
                            if self.triple_containing(self.matrix[rng[int(sector / 3)][int(box / 3)]][rng[sector % 3][box % 3]][0], [i, j, k]):
                                triples += 1
                                boxes.append(box)
                            if self.triple_not_containing(self.matrix[rng[int(sector / 3)][int(box / 3)]][rng[sector % 3][box % 3]][0], [i, j, k]):
                                none += 1
                        if triples == 3 and none == 6:
                            flag = flag or self.delete_from_matrix_sectors(sector, boxes, [i, j, k])
        return flag

    def hidden_triples(self):
        flag = False
        flag1 = True
        while flag1:
            flag2 = True
            while flag2:
                flag3 = self.hidden_triples_rows()
                flag2 = self.hidden_triples_columns()
                flag = flag or flag2 or flag3
            flag1 = self.hidden_triples_sectors()
            flag = flag or flag1
        return flag

    def solve(self):
        if not self.hidden_singles_flag and self.steps:
            self.show_sudoku_grid()
        i = 0
        while i < 9:
            j = 0
            while j < 9:
                if self.matrix[i][j][1] == 0 and len(self.matrix[i][j][0]) == 1:
                    self.changes = []
                    self.changes.append([i, j])
                    self.matrix[i][j][1] = 1
                    if self.steps:
                        print(("{}. NAKED SINGLE {} IN [{}, {}]").format(self.step_counter, self.matrix[i][j][0][0], i + 1, j + 1))
                        self.step_counter += 1
                    self.update()
                    if self.steps:
                        self.show_sudoku_grid()
                    i = 0
                    j = 0
                else:
                    j += 1
            i += 1
        self.hidden_singles_flag = False
        if self.single_possible_digits():
            self.hidden_singles_flag = True
            self.solve()
        if self.locked_candidates_type1():
            self.solve()
        if self.locked_candidates_type2():
            self.solve()
        if self.naked_pairs():
            self.solve()
        if self.naked_triples():
            self.solve()
        if self.hidden_pairs():
            self.solve()
        if self.hidden_triples():
            self.solve()

    def show_sudoku(self):
        print("-" * 25)
        for i in range(9):
            print(("|" + " {} {} {} |" * 3).format(*[self.matrix[i][j][0][0] if self.matrix[i][j][1] == 1 else "." for j in range(9)]))
            if i == 8:
                print("-" * 25)
            elif i % 3 == 2:
                print("|" + "-" * 23 + "|")
        print('\n')

    def show_sudoku_grid1(self):
        print("")
        print("-" * 91)
        for i in range(9):
            line = "|"
            for j in range(9):
                if self.matrix[i][j][1] == 0:
                    for k in range(int((9 - len(self.matrix[i][j][0])) / 2)):
                        line += ' '
                    for digit in self.matrix[i][j][0]:
                        line += str(digit)
                    for k in range(9 - len(self.matrix[i][j][0]) - int((9 - len(self.matrix[i][j][0])) / 2)):
                        line += ' '
                    if j % 3 == 2:
                        line += "|"
                    else:
                        line += "."
                else:
                    line += " " * 9
                    if j % 3 == 2:
                        line +=  "|"
                    else:
                        line += "."
            print(line)
            line = "|"
            for j in range(9):
                if self.matrix[i][j][1] == 0:
                    line += (" " * 9)
                else:
                    line += ("    {}    ").format(self.matrix[i][j][0][0])
                if j % 3 == 2:
                    line += "|"
                else:
                    line += "."
            print(line)
            line = "|"
            for j in range(9):
                line += "         "
                if j % 3 == 2:
                    line += "|"
                else:
                    line += "."
            print(line)
            if i % 3 == 2:
                print("-" * 91)
            else:
                print("| . . . . . . . . . . . . . . " * 3 + "|")
        print("")

    def show_sudoku_grid(self):
        pygame.init()
        size = 600
        screen = pygame.display.set_mode((size + 2, size + 2))
        screen.fill((255, 255, 255))
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            draw(screen, size, self.matrix)
            pygame.display.flip()


    def backtracking(self):
        self.solve()
        minimum = 10
        minimum_coords = []
        for i in range(9):
            for j in range(9):
                if self.matrix[i][j][1] == 0:
                    if len(self.matrix[i][j][0]) < minimum:
                        minimum = len(self.matrix[i][j][0])
                        minimum_coords = [i, j]
        if minimum > 1 and minimum < 10:
            possibilities = self.matrix[minimum_coords[0]][minimum_coords[1]][0][:]
            backup = deepcopy(self.matrix.copy())
            for number in possibilities:
                self.matrix[minimum_coords[0]][minimum_coords[1]][0] = [number]
                self.matrix[minimum_coords[0]][minimum_coords[1]][1] = 1
                self.changes = [minimum_coords[:]]
                self.recursion_executions += 1
                if self.steps:
                    print("\n")
                    print(("{}. BACKTRACKING - DIGIT {} IN [{}, {}]").format(self.step_counter, number, minimum_coords[0] + 1, minimum_coords[1] + 1))
                    self.step_counter += 1
                self.update()
                self.backtracking()
                self.matrix = deepcopy(backup.copy())
        elif minimum == 0:  #return
            if self.steps:
                print("\n")
                print(("{}. CONTRADICTORY SOLUTION").format(self.step_counter))
                print("\n")
                self.step_counter += 1
            return 0
        elif minimum == 10: #boundary condition
            print("SOLUTION")
            self.show_sudoku()
            print("How many times backtracking was executed: ", self.recursion_executions)
            print('\n')
            self.steps = False
            return 0

def main(file, show=True):
    grid = Predict.main(file, show)
    a = Sudoku(grid, True)
    print("PRIMARY GRID")
    a.show_sudoku()
    a.backtracking()

