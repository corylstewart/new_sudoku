from EnhancedHandler import EnhancedHandler as EH
import sudoku_db as SDB


class SudokuHtmlBuilder:
    def make_cell_type(self,puzzle,i,j):
        cell_value = puzzle[(i*8)+j]
        if cell_value <> '0':
            return 'readonly value='+cell_value
        else:
            return 'maxlength=1 onblur=j8(this)'

    def make_td_class(self,i,j):
        td_class = 'class='
        if i in [0,3,6]:
            td_class += 'top'
        elif i == 8:
            td_class += 'bot'
        else:
            td_class += 'mid'
        if j in [0,3,6]:
            td_class += 'left'
        elif j == 8:
            td_class += 'rght'
        else:
            td_class += 'midl'
        return td_class

    def make_input_class(self,puzzle,i,j):
        cell_value = puzzle[(i*8)+j]
        if cell_value == '0':
            return 'class=emptycell'
        else:
            return 'class=full_cell'

    def build_html(self, arg_dict):
        for i in range(9):
            for j in range(9):
                arg_dict['celltype'+str(i)+str(j)] = self.make_cell_type(arg_dict['puzzle'],i,j)
                arg_dict['ca'+str(i)+str(j)] = self.make_td_class(i,j)
                arg_dict['cb'+str(i)+str(j)] = self.make_input_class(arg_dict['puzzle'],i,j)

class SudokuLevelHandler(EH.EnhancedHandler):
    def get(self):
        self.arg_dict['level'] = 'user'

        if self.arg_dict['level'] == 'user':
            self.arg_dict['puzzle_solution'] = '0'*81
            self.arg_dict['puzzle'] = '0'*81
        else:
            levels = {'easy':1, 'medium':2, 'hard':3}
            puzzle = SDB.SudokuDb().get_random_puzzle_by_level(levels[self.arg_dict['level']])
            self.arg_dict['name'] = 'Cory'
            self.arg_dict['puzzle_solution'] = puzzle.solution     
            self.arg_dict['puzzle'] = puzzle.grid
        SudokuHtmlBuilder().build_html(self.arg_dict)
        self.render('Newer Sudoku.html', **self.arg_dict)


class SudokuUserGeneratedHandler(EH.EnhancedHandler):
    def get(self):
        self.arg_dict['level'] = 'user'
        self.arg_dict['puzzle_solution'] = '0'*81
        self.arg_dict['puzzle'] = '0'*81
        SudokuHtmlBuilder().build_html(self.arg_dict)
        self.render('Newer Sudoku.html', **self.arg_dict)

class CreateDB(EH.EnhancedHandler):
    def get(self):
        with open('sudoku_old.txt', 'r') as f:
            for puzzle in f.readlines():
                puzzle = puzzle.split()
                puzzle[2] = int(puzzle[2])
                self.write(puzzle)
                db = SDB.SudokuDb()
                db.put_puzzle(puzzle[1], puzzle[0], puzzle[2])

class GetPuzzle(EH.EnhancedHandler):
    def get(self):
        puzzle = SDB.SudokuDb().get_puzzle_by_solution('300000080700003052502708000000025070080430000000007090000000006430056007200000300')
        self.write(puzzle)

class ClearDB(EH.EnhancedHandler):
    def get(self):
        SDB.SudokuDb().delete_sudoku_db()
        self.write('done')


