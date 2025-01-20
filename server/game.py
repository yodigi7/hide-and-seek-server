VISION_VAL = 0
EMPTY_VAL = 1
HIDER_VAL = 2
SEEKER_VAL = 3
VISION_DISTANCE = 2


class Game:
    def __init__(self):
        self.hider_coords = (0, 0)
        self.seeker_coords = (29, 29)
        self.seeker_move = []
        self.hider_move = []
        self.current_game_step = 0

    def game_step(self):
        if not self._valid_hider_move():
            self.hider_move = []
        if not self._valid_seeker_move():
            self.seeker_move = []
        if self._hider_can_move():
            if len(self.hider_move) > 0:
                self.hider_coords = self.hider_move
                self.hider_move = []
        if len(self.seeker_move) > 0:
            self.seeker_coords = self.seeker_move
            self.seeker_move = []
        self.current_game_step += 1

    def _valid_hider_move(self):
        return self.valid_hider_move(self.hider_move)

    def valid_hider_move(self, move):
        return self.valid_move(move, self.hider_coords)

    def _valid_seeker_move(self):
        return self.valid_seeker_move(self.seeker_move)

    def valid_seeker_move(self, move):
        return self.valid_move(move, self.seeker_coords)

    def is_over(self):
        return self.seeker_coords == self.hider_coords

    def valid_move(self, dest, start):
        return dest and len(dest) and manhattan_distance(dest, start) == 1

    def get_board(self):
        board = [[VISION_VAL for _ in range(30)] for _ in range(30)]
        board[self.hider_coords[0]][self.hider_coords[1]] = HIDER_VAL
        board[self.seeker_coords[0]][self.seeker_coords[1]] = SEEKER_VAL
        return board

    def get_board_seeker(self):
        if self.seeker_can_see():
            return self.get_board()
        board = [
            [
                (
                    VISION_VAL
                    if manhattan_distance(self.seeker_coords, (i, j)) <= 2
                    else EMPTY_VAL
                )
                for j in range(30)
            ]
            for i in range(30)
        ]
        board[self.seeker_coords[0]][self.seeker_coords[1]] = SEEKER_VAL
        if manhattan_distance(self.seeker_coords, self.hider_coords) <= 2:
            board[self.hider_coords[0]][self.hider_coords[1]] = HIDER_VAL
        return board

    def _hider_can_move(self):
        return self.current_game_step % 2

    def seeker_can_see(self):
        """
        Check the current game step to see if the seeker can see the whole board or not
        Returns:
            bool: Returns whether the seeker can see the whole board or not
        """
        return self.current_game_step % 20 < 3


def manhattan_distance(coord1, coord2):
    """
    Calculate the Manhattan distance between two coordinates.

    Args:
        coord1 (tuple): The first coordinate (x1, y1).
        coord2 (tuple): The second coordinate (x2, y2).

    Returns:
        int: The Manhattan distance between coord1 and coord2.
    """
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])
