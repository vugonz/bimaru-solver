# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys
import numpy

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


HINTS = []

class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

class Board:
    def __init__(self,
                 table: numpy.ndarray,
                 rows: list,
                 cols: list,
                 hints: list,
                 ships: list,
                 has_hints: bool,
                 ):
        self.table = table
        self.rows = rows
        self.cols = cols
        self.hints = hints
        self.ships = ships
        self.is_valid = True
        self.has_hints = has_hints

    def action(self, row, col, operation, size=0):
        new_board = self.board_copy()

        if operation == "v":
            new_board.add_vertical_ship(row, col, size)
        elif operation == "h":
            new_board.add_horizontal_ship(row, col, size)
        elif operation == "w":
            new_board.add_water(row, col)
        else:
            new_board.add_single_ship(row, col)

        return new_board

    def is_valid_action(self, row, col, operation, size=0):
        if operation == "v":
            # ship will fall out
            if row + size > 10:
                return False

            # no space in col
            if self.cols[col] < size:
                return False

            # rows have no space
            for i in range(row, row + size):
                if not self.rows[i]:
                    return False

            if not self.is_valid_top_cell(row, col):
                return False

            i = 1
            for i in range(2, size):
                if not self.is_valid_vertical_middle_cell(row + i - 1, col):
                    return False

            return self.is_valid_bottom_cell(row + i, col)

        elif operation == "h":
            # ship will fall out
            if col + size > 10:
                return False

            # no space in col
            if self.rows[row] < size:
                return False

            # cols have no space
            for i in range(col, col + size):
                if not self.cols[i]:
                    return False

            if not self.is_valid_left_cell(row, col):
                return False

            i = 1
            for i in range(2, size):
                if not self.is_valid_horizontal_middle_cell(row, col + i - 1):
                    return False

            return self.is_valid_right_cell(row, col + i)

        elif operation == "c":
            return self.is_valid_center_cell(row, col)
        # water operations are always valid
        else:
            return True

    def get_valid_actions(self):
        if self.has_hints:
            return self.get_hint_actions(*self.hints.pop())

        actions = []

        size = 0
        # get ship
        for c in range(len(self.ships)):
            # iterate in reverse order
            if self.ships[-(c + 1)]:
                size = 4 - (c % 4)
                break

        if size == 0:
            print("never reached")

        for i in range(10):
            if not self.rows[i]:
                continue
            for j in range(10):
                if not self.cols[j]:
                    continue
                if self.table[i][j] == ".":
                    if size == 1:
                        actions.append((i, j, "c"))
                    else:
                        actions.append((i, j, "v", size))
                        actions.append((i, j, "h", size))
                    #actions.append((i, j, "w"))

        return [action for action in actions if self.is_valid_action(*action)]

    def get_hint_actions(self, row: int, col: int, letter: str):
        actions = []

        if letter == "L":
            for i in range(2, 5):
                # no ships left
                if not self.ships[i - 1]:
                    continue
                actions.append((row, col, "h", i))
                # remove duplicate hints to this ship
                for hint in self.hints:
                    if hint[0] != row: # different row
                        continue
                    for x in range(1, i):
                        if hint[1] == col + x:
                            self.hints.remove(hint)
                            break
        elif letter == "T":
            for i in range(2, 5):
                if not self.ships[i - 1]:
                    continue
                actions.append((row, col, "v", i))
                for hint in self.hints:
                    if hint[1] != col:
                        continue
                    for x in range(1, i):
                        if hint[0] == row + x:
                            self.hints.remove(hint)
                            break
        elif letter == "R":
            for i in range(2, 5):
                if not self.ships[i - 1]:
                    continue
                actions.append((row, col - i + 1, "h", i))
                for hint in self.hints:
                    if hint[0] != row:
                        continue
                    for x in range(1, i):
                        if hint[1] == col - x:
                            self.hints.remove(hint)
                            break
        elif letter == "B":
            for i in range(2, 5):
                if not self.ships[i - 1]:
                    continue
                actions.append((row - i + 1, col, "v", i))
                for hint in self.hints:
                    if hint[1] != col:
                        continue
                    for x in range(1, i):
                        if hint[0] == row - x:
                            self.hints.remove(hint)
                            break

        elif letter == "M":
            if self.ships[2]:
                actions.append((row - 1, col, "v", 3))
                actions.append((row, col - 1, "h", 3))
            if self.ships[3]:
                actions.append((row - 1, col, "v", 4))
                actions.append((row - 2, col, "v", 4))
                actions.append((row, col - 1, "h", 4))
                actions.append((row, col - 2, "h", 4))

        return [action for action in actions if self.is_valid_action(*action)]

    def is_complete(self):
        return all(x == 0 for x in self.ships + self.cols + self.rows)

    #############
    # Actions
    #############
    def add_horizontal_ship(self, row, col, size):
        self.ships[size - 1] -= 1

        self.rows[row] -= size

        self.add_left_cell(row, col)
        self.cols[col] -= 1

        # add middle
        i = 0
        for i in range(1, size - 1):
            self.add_middle_horizontal_cell(row, col + i)
            self.cols[col + i] -= 1

        self.add_right_cell(row, col + i + 1)
        self.cols[col + i + 1] -= 1

    def add_vertical_ship(self, row, col, size):
        self.ships[size - 1] -= 1

        self.cols[col] -= size

        self.add_top_cell(row, col)
        self.rows[row] -= 1

        # add middle
        i = 0
        for i in range(1, size - 1):
            self.add_middle_vertical_cell(row + i, col)
            self.rows[row + i] -= 1

        self.add_bottom_cell(row + i + 1, col)
        self.rows[row + i + 1] -= 1

    def add_single_ship(self, row, col):
        self.ships[0] -= 1

        self.rows[row] -= 1
        self.cols[col] -= 1

        self.add_center_cell(row, col)

    def add_water(self, row, col):
        self.add_water_cell(row, col)

    #########################
    # Piece adders
    #########################
    def add_left_cell(self, row, col):
        self.table[row][col] = "l"
        # diagonals
        self.set_diagonals(row, col, "w")
        # vertical
        self.set_vertical(row, col, "w")
        # left
        self.set_cell(row, col - 1, "w")

    def add_middle_horizontal_cell(self, row, col):
        self.table[row][col] = "m"
        self.set_cell(row - 1, col + 1, "w")
        self.set_cell(row + 1, col + 1, "w")

    def add_right_cell(self, row, col):
        self.table[row][col] = "r"
        self.set_cell(row - 1, col + 1, "w")
        self.set_cell(row + 1, col + 1, "w")
        self.set_cell(row, col + 1, "w")

    def add_top_cell(self, row, col):
        self.table[row][col] = "t"
        # diagonals
        self.set_diagonals(row, col, "w")
        # horizontal
        self.set_horizontal(row, col, "w")
        # top
        self.set_cell(row - 1, col, "w")

    def add_middle_vertical_cell(self, row, col):
        self.table[row][col] = "m"
        self.set_cell(row + 1, col - 1, "w")
        self.set_cell(row + 1, col + 1, "w")

    def add_bottom_cell(self, row, col):
        self.table[row][col] = "b"
        self.set_cell(row + 1, col - 1, "w")
        self.set_cell(row + 1, col + 1, "w")
        self.set_cell(row + 1, col, "w")

    def add_center_cell(self, row, col):
        self.table[row][col] = "c"
        self.set_horizontal(row, col, "w")
        self.set_vertical(row, col, "w")
        self.set_diagonals(row, col, "w")

    def add_water_cell(self, row, col):
        self.table[row][col] = "w"

    #####################
    # Cell validators
    #####################
    def is_valid_center_cell(self, row, col):
        if self.get_value(row, col) != ".":
            return False

        vertical = self.adjacent_vertical_values(row, col)
        horizontal = self.adjacent_horizontal_values(row, col)
        diagonal = self.adjacent_diagonal_values(row, col)

        return all(x in [".", "w", "i"] for x in vertical + horizontal + diagonal)

    def is_valid_left_cell(self, row, col):
        if self.get_value(row, col) not in [".", "l"]:
            return False

        left, right = self.adjacent_horizontal_values(row, col)

        if right not in [".", "m", "r"]:
            return False

        vertical = self.adjacent_vertical_values(row, col)
        diagonal = self.adjacent_diagonal_values(row, col)

        return all(x in [".", "w", "i"] for x in vertical + diagonal + (left,))

    def is_valid_horizontal_middle_cell(self, row, col):
        if self.get_value(row, col) not in [".", "m"]:
            return False

        if self.get_value(row, col + 1) not in [".", "m", "r"]:
            return False

        up_right_diag = self.get_value(row - 1, col + 1)
        down_right_diag = self.get_value(row + 1, col + 1)

        return all(x in [".", "w", "i"] for x in (up_right_diag, down_right_diag))

    def is_valid_right_cell(self, row, col):
        if self.get_value(row, col) not in [".", "r"]:
            return False

        up_right_diagonal = self.get_value(row - 1, col + 1)
        down_right_diagonal = self.get_value(row + 1, col + 1)

        right = self.get_value(row, col + 1)

        return all(x in [".", "w", "i"] for x in (up_right_diagonal, right, down_right_diagonal))

    def is_valid_top_cell(self, row, col):
        if self.get_value(row, col) not in [".", "t"]:
            return False

        top, bottom = self.adjacent_vertical_values(row, col)

        if bottom not in [".", "m", "b"]:
            return False

        horizontal = self.adjacent_horizontal_values(row, col)
        diagonal = self.adjacent_diagonal_values(row, col)

        return all(x in [".", "w", "i"] for x in horizontal + diagonal + (top,))

    def is_valid_vertical_middle_cell(self, row, col):
        if self.get_value(row, col) not in [".", "m"]:
            return False

        if self.get_value(row + 1, col) not in [".", "m", "b"]:
            return False

        down_left_diag = self.get_value(row + 1, col - 1)
        down_right_diag = self.get_value(row + 1, col + 1)

        return all(x in [".", "w", "i"] for x in (down_left_diag, down_right_diag))

    def is_valid_bottom_cell(self, row, col):
        if self.get_value(row, col) not in [".", "b"]:
            return False

        down_left_diagonal = self.get_value(row + 1, col - 1)
        down_right_diagonal = self.get_value(row + 1, col + 1)

        bottom = self.get_value(row + 1, col)

        return all(x in [".", "w", "i"] for x in (down_left_diagonal, bottom, down_right_diagonal))

    #################
    # Setters
    #################
    def set_cell(self, row, col, letter):
        if 0 <= row < 10 and 0 <= col < 10:
            self.table[row][col] = letter

    def set_diagonals(self, row, col, letter):
        self.set_cell(row - 1, col - 1, letter)
        self.set_cell(row + 1, col - 1, letter)
        self.set_cell(row + 1, col + 1, letter)
        self.set_cell(row - 1, col + 1, letter)

    def set_horizontal(self, row, col, letter):
        self.set_cell(row, col - 1, letter)
        self.set_cell(row, col + 1, letter)

    def set_vertical(self, row, col, letter):
        self.set_cell(row - 1, col, letter)
        self.set_cell(row + 1, col, letter)

    #################
    # Getters
    #################
    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if 0 <= row < 10 and 0 <= col < 10:
            return self.table[row][col]

        # for invalid
        return "i"

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return self.get_value(row - 1, col), self.get_value(row + 1, col)

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return self.get_value(row, col - 1), self.get_value(row, col + 1)

    def adjacent_diagonal_values(self, row: int, col: int):
        """ Returns diagonal values starting at top left and going counter clockwise """
        return \
            self.get_value(row - 1, col - 1), \
                self.get_value(row + 1, col - 1), \
                self.get_value(row + 1, col + 1), \
                self.get_value(row - 1, col + 1)

    def board_copy(self):
        table = numpy.copy(self.table)
        rows = self.rows.copy()
        cols = self.cols.copy()
        ships = self.ships.copy()
        hints = self.hints.copy()

        return Board(table, rows, cols, hints, ships, len(self.hints) != 0)

    @classmethod
    def parse_instance(cls):
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.
        """
        rows, cols, _, *raw_hints = sys.stdin.readlines()

        rows = list(map(int, rows.split()[1:]))
        cols = list(map(int, cols.split()[1:]))
        hints = []

        table = numpy.chararray((10, 10), unicode=True)
        table[:] = "."

        ships = [4, 3, 2, 1]

        for hint in raw_hints:
            x, y, letter = hint.split()[1:]
            x, y = int(x), int(y)
            table[x][y] = letter.lower()
            HINTS.append((x, y, letter))

            # don't add water to hints
            if letter != "W":
                # decrease row and col counts
                if letter == "C":
                    ships[0] -= 1
                    rows[x] -= 1
                    cols[y] -= 1
                # append hints not yet added
                else:
                    hints.append((x, y, letter))

        return cls(table, rows, cols, hints, ships, len(hints) != 0)

    def __str__(self):
        # fill hints
        for hint in HINTS:
            self.table[hint[0]][hint[1]] = hint[2]

        return "\n".join("".join(cell for cell in row) for row in self.table).replace("w", ".")

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = BimaruState(board)
        super().__init__(state)

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        if not state.board.is_valid:
            return []

        actions = state.board.get_valid_actions()
        return actions

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        return BimaruState(state.board.action(*action))

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #print(state.board)
        return state.board.is_complete()

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        raise NotImplemented

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Bimaru(board)
    goal = depth_first_tree_search(problem)
    print(goal.state.board)
    a = 1
