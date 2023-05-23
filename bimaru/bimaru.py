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


class InvalidCell(Exception):
    ...


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    def __init__(self,
                 table: numpy.chararray,
                 rows: list,
                 cols: list,
                 hints: list,
                 ships: list,
                 ):
        self.table = table
        self.rows = rows
        self.cols = cols
        self.hints = hints
        self.ships = ships
        self.is_valid = True
        self.has_hints = True

    def get_valid_actions(self):
        if self.has_hints:
            return self.get_hints_actions()

        pass

    def get_hint_actions(self):
        ...

    #############
    # Actions
    #############
    def add_horizontal_ship(self, row, col, size):
        self.rows[row] -= size
        self.ships[size - 1] -= 1

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
        self.cols[col] -= 1
        self.rows[row] -= 1

        self.add_center_cell(row, col)

    def add_water(self, row, col):
        self.add_water_cell(row, col)

    #########################
    # Piece adders
    #########################
    def add_left_cell(self, row, col):
        if not self.is_valid_left_cell(row, col):
            raise InvalidCell
        self.table[row][col] = "l"
        # diagonals
        self.set_diagonals(row, col, "w")
        # vertical
        self.set_vertical(row, col, "w")
        # left
        self.set_cell(row, col - 1, "w")

    def add_middle_horizontal_cell(self, row, col):
        if not self.is_valid_horizontal_middle_cell(row, col):
            raise InvalidCell

        self.table[row][col] = "m"
        self.set_cell(row - 1, col + 1, "w")
        self.set_cell(row + 1, col + 1, "w")

    def add_right_cell(self, row, col):
        if not self.is_valid_right_cell(row, col):
            raise InvalidCell
        self.table[row][col] = "r"
        self.set_cell(row - 1, col + 1, "w")
        self.set_cell(row + 1, col + 1, "w")
        self.set_cell(row, col + 1, "w")

    def add_top_cell(self, row, col):
        if not self.is_valid_top_cell(row, col):
            raise InvalidCell
        self.table[row][col] = "t"
        # diagonals
        self.set_diagonals(row, col, "w")
        # horizontal
        self.set_horizontal(row, col, "w")
        # top
        self.set_cell(row - 1, col, "w")

    def add_middle_vertical_cell(self, row, col):
        if not self.is_valid_vertical_middle_cell(row, col):
            raise InvalidCell
        self.table[row][col] = "m"
        self.set_cell(row + 1, col - 1, "w")
        self.set_cell(row + 1, col + 1, "w")

    def add_bottom_cell(self, row, col):
        if not self.is_valid_bottom_cell(row, col):
            raise InvalidCell
        self.table[row][col] = "b"
        self.set_cell(row + 1, col - 1, "w")
        self.set_cell(row + 1, col + 1, "w")
        self.set_cell(row + 1, col, "w")

    def add_center_cell(self, row, col):
        if not self.is_valid_center_cell(row, col):
            raise InvalidCell

        self.table[row][col] = "c"
        self.set_horizontal(row, col, "w")
        self.set_vertical(row, col, "w")
        self.set_diagonals(row, col, "w")

    def add_water_cell(self, row, col):
        if not self.table[row][col] == "*":
            raise InvalidCell

        self.table[row][col] = "w"

    #####################
    # Cell validators
    #####################
    def is_valid_center_cell(self, row, col):
        if self.get_value(row, col) != "*":
            return False

        vertical = self.adjacent_vertical_values(row, col)
        horizontal = self.adjacent_horizontal_values(row, col)
        diagonal = self.adjacent_diagonal_values(row, col)

        return all(x in ["*", "w", "i"] for x in vertical + horizontal + diagonal)

    def is_valid_left_cell(self, row, col):
        if self.get_value(row, col) not in ["*", "l"]:
            return False

        left, right = self.adjacent_horizontal_values(row, col)

        if right not in ["*", "m", "r"]:
            return False

        vertical = self.adjacent_vertical_values(row, col)
        diagonal = self.adjacent_diagonal_values(row, col)

        return all(x in ["*", "w", "i"] for x in vertical + diagonal + (left,))

    def is_valid_horizontal_middle_cell(self, row, col):
        if self.get_value(row, col) not in ["*", "m"]:
            return False

        if self.get_value(row, col + 1) not in ["*", "m", "r"]:
            return False

        up_right_diag = self.get_value(row - 1, col + 1)
        down_right_diag = self.get_value(row + 1, col + 1)

        return all(x in ["*", "w"] for x in (up_right_diag, down_right_diag))

    def is_valid_right_cell(self, row, col):
        if self.get_value(row, col) not in ["*", "r"]:
            return False

        up_right_diagonal = self.get_value(row - 1, col + 1)
        down_right_diagonal = self.get_value(row + 1, col + 1)

        right = self.get_value(row, col + 1)

        return all(x in ["*", "w", "i"] for x in (up_right_diagonal, right, down_right_diagonal))

    def is_valid_top_cell(self, row, col):
        if self.get_value(row, col) not in ["*", "t"]:
            return False

        top, bottom = self.adjacent_vertical_values(row, col)

        if bottom not in ["*", "m", "b"]:
            return False

        horizontal = self.adjacent_horizontal_values(row, col)
        diagonal = self.adjacent_diagonal_values(row, col)

        return all(x in ["*", "w", "i"] for x in horizontal + diagonal + (top,))

    def is_valid_vertical_middle_cell(self, row, col):
        if self.get_value(row, col) not in ["*", "m"]:
            return False

        if self.get_value(row + 1, col) not in ["*", "m", "b"]:
            return False

        down_left_diag = self.get_value(row + 1, col - 1)
        down_right_diag = self.get_value(row + 1, col + 1)

        return all(x in ["*", "w"] for x in (down_left_diag, down_right_diag))

    def is_valid_bottom_cell(self, row, col):
        if self.get_value(row, col) not in ["*", "b"]:
            return False

        down_left_diagonal = self.get_value(row + 1, col - 1)
        down_right_diagonal = self.get_value(row + 1, col + 1)

        bottom = self.get_value(row + 1, col)

        return all(x in ["*", "w", "i"] for x in (down_left_diagonal, bottom, down_right_diagonal))

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

    def __str__(self):
        ...

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
        table[:] = "*"

        ships = [4, 3, 2, 1]

        for hint in raw_hints:
            x, y, letter = hint.split()[1:]
            x, y = int(x), int(y)
            table[x][y] = letter.lower()

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

        return cls(table, rows, cols, hints, ships)


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = BimaruState(board)
        super().__init__(state)

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Bimaru(board)
    while 1:
        continue
    a = 1
