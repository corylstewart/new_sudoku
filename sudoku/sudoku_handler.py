from EnhancedHandler import EnhancedHandler as EH
import sudoku_db as SDB
from board import SolvePuzzle

class SudokuHtmlCell:
    '''Takes as input the location of a cell and its value to create an object
    with the atrributes for that paticular cell.'''
    def __init__(self, loc, value):
        self.value = value
        self.loc = loc
        self.i = int(loc[0])
        self.j = int(loc[1])
        self.td_class = self.make_td_class()
        self.td_name = 'name=td'+self.loc
        self.td_id = 'id=td'+self.loc
        self.in_class = self.make_input_class()
        self.in_name = 'name=in'+self.loc
        self.in_id = 'id=in'+self.loc
        self.in_type = self.make_in_type()
        
    def make_td_class(self):
        td_class = 'class='
        if self.i in [0,3,6]:
            td_class += 'top'
        elif self.i == 8:
            td_class += 'bot'
        else:
            td_class += 'mid'
        if self.j in [0,3,6]:
            td_class += 'left'
        elif self.j == 8:
            td_class += 'rght'
        else:
            td_class += 'midl'
        return td_class

    def make_input_class(self):
        if self.value == '0':
            return 'class=emptycell'
        else:
            return 'class=full_cell'

    def make_in_type(self):
        if self.value <> '0':
            return 'readonly value='+self.value
        else:
            return 'maxlength=1 onblur=remove_space(this)'


class SudokuHtmlBuilder:
    '''Takes as input a puzzle string and returns a 9X9 arrays of SudokuHtmlCell
    object based on the puzzle string'''
    def build_html(self,puzzle):
        cells = []
        for i in range(9):
            cells.append([])
            for j in range(9):
                loc = str(i)+str(j)
                value = puzzle[(i*9)+j:((i*9)+j+1)]
                cells[i].append(SudokuHtmlCell(loc, value))
        return cells


class SudokuLevelHandler(EH.EnhancedHandler):
    def get(self):
        self.arg_dict['level'] = self.request.get('level')
        levels = {'user':0, 'easy':1, 'medium':2, 'hard':3}
        if not self.arg_dict['level'] or self.arg_dict['level'] not in levels:
            self.arg_dict['level'] = 'easy'
        if self.arg_dict['level'] == 'user':
            self.arg_dict['puzzle_solution'] = '0'*81
            self.arg_dict['puzzle'] = '0'*81
        else:            
            puzzle = SDB.SudokuDb().get_random_puzzle_by_level(levels[self.arg_dict['level']])
            self.arg_dict['puzzle_solution'] = puzzle.solution     
            self.arg_dict['puzzle'] = puzzle.grid
        self.arg_dict['cell_html'] = SudokuHtmlBuilder().build_html(self.arg_dict['puzzle'])
        self.render('sudoku.html', **self.arg_dict)

    def post(self):
        self.arg_dict['level'] = 'user'
        self.arg_dict['user_solved'] = 'true'
        self.arg_dict['puzzle'] = self.request.get('user_puzzle_input_name')
        puzzle = SolvePuzzle(self.arg_dict['puzzle'])
        if not puzzle.is_valid():
            self.arg_dict['user_solved'] = 'not valid'
        else:
            puzzle.solve_puzzle()           
            if not puzzle.is_solved():
                self.arg_dict['user_solved'] = 'not solved'
        puzzle._make_solution_string()
        self.arg_dict['puzzle_solution'] = puzzle.solution_string
        self.arg_dict['puzzle'] = puzzle.solution_string
        self.arg_dict['cell_html'] = SudokuHtmlBuilder().build_html(self.arg_dict['puzzle'])
        if puzzle.difficulty in [1,2,3]:
            sdb = SDB.SudokuDb()
            if not sdb.get_puzzle_by_grid(self.arg_dict['puzzle']):
                sdb.put_puzzle(self.arg_dict['puzzle'],puzzle.solution_string,
                               puzzle.difficulty,self.user)
        self.render('sudoku.html', **self.arg_dict)


class CreateDB(EH.EnhancedHandler):
    def get(self):
        if self.check_super_user():
            with open('sudoku_old.txt', 'r') as f:
                for puzzle in f.readlines():
                    puzzle = puzzle.split()
                    puzzle[2] = int(puzzle[2])
                    self.write('working')
                    db = SDB.SudokuDb()
                    db.put_puzzle(puzzle[1], puzzle[0], puzzle[2])
            self.write('done')

class GetPuzzle(EH.EnhancedHandler):
    def get(self):
        puzzle = SDB.SudokuDb().get_puzzle_by_solution('300000080700003052502708000000025070080430000000007090000000006430056007200000300')
        self.write(puzzle)

class ClearDB(EH.EnhancedHandler):
    def get(self):
        if self.check_super_user():
            SDB.SudokuDb().delete_sudoku_db()
            self.write('done')


