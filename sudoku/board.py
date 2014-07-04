import copy
import time

class BlankBoard():
    def __init__(self):
        self.board = self._make_empty_board()
        self._cells = [str(x) for x in xrange(9)]
        self.rows = [[row+col for col in self._cells] for row in self._cells]
        self.cols = [[col+row for col in self._cells] for row in self._cells]
        self.squares = self._make_squares()
        self.groupings = [self.rows, self.cols, self.squares]

    def _make_empty_board(self):
        board = {}
        for row in xrange(9):
            for col in xrange(9):
                board[str(row)+str(col)] = 0
        return board

    def _make_squares(self):
        square = []
        squares = []
        for y in xrange(0,3):
            for z in xrange(0,3):
                for i in xrange(0,3):
                    for j in xrange(0,3):
                        square.append(str(i+(y*3))+str(j+(z*3)))
                squares.append(square)
                square = []
        return squares



class SolvePuzzle(BlankBoard):
    def __init__(self,grid_str):
        self.board = BlankBoard()
        self.grid_str = grid_str
        self._read_grid()
        self.board.board_with_lists = self._place_lists()
        self.solution_string = None
        self.difficulty = 0
        self.layers = [self._remove_numbers,
                       self._remove_lonely_numbers,
                       self._remove_sets,
                       self._remove_hidden_pairs]


    def _read_grid(self):
        if len(self.grid_str) <> 81:
            return
        puzzle_str = [[x for x in row] for row in 
                      [self.grid_str[i:i+9] for i in range(0,81,9)]]
        for row in xrange(9):
            for col in xrange(9):
                self.board.board[str(row)+str(col)] = int(puzzle_str[row][col])

    def _place_lists(self):
        board_with_lists = {}
        for cell,value in self.board.board.items():
            if value == 0:
                board_with_lists[cell] = range(1,10)
            else:
                board_with_lists[cell] = value
        return board_with_lists

    def is_valid(self):
        count = 0
        for cell, value in self.board.board_with_lists.items():
            if isinstance(value,int):
                count += 1
        if count < 17:
            return False
        return self._apply_true_false(self._valid_count)

    def valid_group(self,group):
        for i in xrange(1,10):
            if group.count(i) > 1:
                return False
        return True

    def _apply_true_false(self,f):
        for group in self.board.groupings:
            for g in group:
                if not f(self._make_group(g)):
                    return False
        return True

    def _make_group(self, grouping):
        return [self.board.board_with_lists[g] for g in grouping]

    def _valid_count(self,group):
        for i in xrange(1,10):
            if group.count(i) > 1:
                return False
        return True

    def is_solved(self):
        if not self.is_valid():
            return False
        for cell, value in self.board.board_with_lists.items():
            if value == 0 or isinstance(value,list):
                return False
        return True

    def _remove_numbers(self,group):
        for g in group:           
            if isinstance(g,int):
                for other in group:
                    if isinstance(other,list) and g in other:
                        other.remove(g)

    def _remove_lonely_numbers(self,group):
        numbers_in_lists = []
        for g in group:
            if isinstance(g,list):
                numbers_in_lists += g
            else:
                numbers_in_lists.append(g)
        nums_to_remove = []
        for num in xrange(1,10):
            if numbers_in_lists.count(num) == 1 and num not in group:
                nums_to_remove.append(num)
        for num in nums_to_remove:
            for g in group:
                if isinstance(g,list) and num in g:
                    while len(g) > 0:
                        g.pop()
                    g.append(num)

    def _remove_sets(self,group):
        seen_it = []
        for i in range(2,5):
            for g in group:
                set_members = []
                if isinstance(g,list) and len(g) == i and group.count(g) == i and g not in seen_it:
                    seen_it.append(g)
                    for j in range(len(group)):
                        if group[j] == g:
                            set_members.append(j)
                    for j in range(len(group)):
                        if j not in set_members and isinstance(group[j],list):
                            for number in group[set_members[0]]:
                                if number in group[j]:
                                    group[j].remove(number)

    def _remove_hidden_pairs(self,group):
        locs = {}
        for i, g in enumerate(group):
            if isinstance(g,list):
                for num in g:
                    if num not in group:
                        if num not in locs:
                            locs[num] = [1,[i]]
                        else:
                            locs[num][0] += 1
                            locs[num][1].append(i)
        for key1,value1 in locs.items():
            for key2,value2 in locs.items():
                if key1 <> key2 and value1 == value2 and value1[0] == 2:
                    old = copy.deepcopy(group)
                    for i in value1[1]:
                        while len(group[i]) > 0:
                            group[i].pop()
                        group[i].append(key1)
                        group[i].append(key2)
                        group[i].sort()

    def _remove_singletons(self):
        for cell, value in self.board.board_with_lists.items():
            if isinstance(value,list) and len(value) == 1:
                self.board.board_with_lists[cell] = value[0]
                self.board.board[cell] = value[0]

    def _apply_maniputlation(self, f):
        for group in self.board.groupings:
            for g in group:
                f(self._make_group(g))
                self._remove_singletons()

    def _make_grid(self):
        grid = []
        for i,row in enumerate(self.board.rows):
            grid.append([])
            for cell in row:
                grid[i].append(self.board.board[cell])
        for row in grid:
            print row

    def _make_solution_string(self):
        self.solution_string = ''
        for row in self.board.rows:
            for cell in row:
                self.solution_string += str(self.board.board[cell])

    def solve_puzzle(self, use_bf=True):
        for i in range(1,len(self.layers)):
            if self.is_solved():
                break
            self.difficulty = i
            old = None
            while old <> self.board.board_with_lists:
                old = copy.deepcopy(self.board.board_with_lists)
                for layer in self.layers[:i+1]:
                    self._apply_maniputlation(layer)
        if not self.is_solved() and use_bf:
            self._make_solution_string()
            self.use_brute_force()

    def use_brute_force(self):
        if self.solution_string:
            puzzle = self.solution_string
        else:
            puzzle = self.grid_str
        puzzle = [int(x) for x in puzzle]
        solution = ''.join([str(x) for x in self.brute_force(puzzle)])
        self._fix_brute_force(solution)

    def brute_force(self, puzzle):
        if puzzle.count(0) == 0:
            return puzzle
        i = puzzle.index(0)
        c = [puzzle[j] for j in range(81)
             if not ((i-j)%9 * (i//9^j//9) * (i//27^j//27 | (i%9//3^j%9//3)))]

        for v in range(1, 10):
            if v not in c:
                r = self.brute_force(puzzle[:i]+[v]+puzzle[i+1:])
                if r is not None:
                    return r

    def _fix_brute_force(self, solution):
        temp_puzzle = self.grid_str
        self.grid_str = solution
        self._read_grid()
        self.board.board_with_lists = self._place_lists()
        self.solution_string = solution
        self.grid_str = temp_puzzle
        self.difficulty = 100
