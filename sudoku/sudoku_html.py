import sudoku_db as sdb
import time
import copy
import grids
import board


class SudokuHtml():
    def __init__(self, grid = [[0 for x in xrange(9)] for x in xrange(9)]):
            self.make_grid(grid)
        
    def make_grid(self,grid):        
        '''value is the value of the sudoku cell, name corresponds to the coordinates in a grid,
        id is what type of cell it is (ie empty, full or wrong, readonly are for cells that are full,
        cheat is whether the cell is showing the value of the cell or not, solution is the actual value of the
        cell, cheat and solution are not currently used but might be used later
        '''
        self.grid = {'value':[], 'name':[], 'id':[],'readonly':[], 'cheat':[], 'solution':[]}
        for i in xrange(len(grid)):
            self.grid['value'].append([])
            self.grid['name'].append([])
            self.grid['id'].append([])
            self.grid['readonly'].append([])
            self.grid['cheat'].append([])
            self.grid['solution'].append([])
            for j in xrange(len(grid[i])):                       
                self.grid['name'][i].append(str(i)+str(j))  #name the cell for its postion in the grid
                self.grid['cheat'][i].append('')
                self.grid['solution'][i].append('')
                if grid[i][j] == 0:                     #if value of the puzzle is zero set the cell to empty
                    self.grid['value'][i].append('')    
                    self.grid['readonly'][i].append('')
                    self.grid['id'][i].append('empty_cell')
                else:
                    self.grid['value'][i].append(grid[i][j])    #if the cell has a value set the cell to full
                    self.grid['readonly'][i].append('readonly ')
                    self.grid['id'][i].append('full_cell')
        self.place_html()

    #cycle over all of the cells and add the style to each cell
    def place_html(self):
        value = self.grid['value']
        name = self.grid['name']
        id = self.grid['id']
        readonly = self.grid['readonly']
        cheat = self.grid['cheat']
        solution = self.grid['solution']
        self.grid['html'] = []
        for i in xrange(len(value)):
            self.grid['html'].append([])
            for j in xrange(len(value[i])):
                s = self.make_style(name[i][j])
                self.grid['html'][i].append(s)

    #create the style for the cells depending on their position in the grid
    def make_style(self, name):
        i = int(name[0])
        j = int(name[1])
        border = 'solid black'
        s = 'margin:0;'
        if i == 0 or i == 3 or i == 6:
            s += 'border-top:' + border + ' 2px;'
        if i == 2 or i == 5 or i == 8:
            s += 'border-bottom:'+ border + ' 2px;'
        if j == 0 or j == 3 or j == 6:
            s += 'border-left:' + border + ' 2px;'
        if j == 2 or j == 5 or j == 8:
            s += 'border-right:' + border + ' 2px;'
        return s



class UserGrid:
    def __init__(self, webpage):
        self.webpage = webpage
        self.user_grid = self.get_grid_from_user()      #get the grid from the user
        self.user_grid_string = board.BoardManipulations().make_grid_string(self.user_grid) #create a grid string from the users grid
        self.user_solution = board.Board(grid = self.user_grid)     #solve the users grid
        self.grid = SudokuHtml(grid = self.user_solution.solution)  #create the HTML for the users solution

    #get the users grid from the input on the webpage
    def get_grid_from_user(self):
        grid = []
        for i in xrange(9):
            grid.append([])
            for j in xrange(9):
                #make sure the cell contains a valid number if not replace it with a zero
                if self.webpage.request.get(str(i)+str(j)).isdigit():
                    grid[i].append(int(self.webpage.request.get(str(i)+str(j))))
                else:
                    grid[i].append(0)
        return grid

class RandomPuzzle:
    def __init__(self, level):
        puzzle = sdb.Sudoku().get_random_puzzle(level)  #query the DB for puzzle of a given level
        self.grid_string = puzzle.grid                  #set the grid string to the puzzle string
        self.solution_string = puzzle.solution          #set the solution to the solution sting
        self.grid = board.BoardManipulations().make_grid(self.grid_string)  #using the grid string create a grid
        self.html = SudokuHtml(self.grid)   #place the html using the grid

class CheckUser:
    def __init__(self, webpage):
        self.webpage = webpage
        self.grid_string = self.webpage.request.get('grid_string')
        self.solution_string = self.webpage.request.get('solution_string')
        self.level = int(self.webpage.request.get('level_string'))
        self.start_time = float(self.webpage.request.get('start_time'))
        self.answer_string = self.get_user_answer()

    #get the values that the user has input into the game and create a string of the values
    def get_user_answer(self):
        answer_string = ''
        for i in xrange(0,9):
            for j in xrange(0,9):
                number = self.webpage.request.get(str(i)+str(j))
                if number:
                    answer_string += number
                else:
                    answer_string += '0'
        return answer_string

    def check_user(self):
        self.get_wrong_locations()      #create a list of the wrong answers
        self.get_correct_locations()    #create a list of the correct answers
        self.count_blanks()             #count how many blanks are still on the board
        self.completetion_time()        #create the string representing the time elapsed
        self.make_congratulations()     #create congratulation note
        self.grid =  board.BoardManipulations().make_grid(self.grid_string)     #convert string to a grid
        self.html = SudokuHtml(self.grid)       #place the HTML
        self.change_html_for_wrong_answers()    #change the HTML for the wrong answers
        self.change_html_for_right_answers()    #change the HTML for the right answers
        self.cells_to_go = self.number_blank + self.number_wrong
        if self.cells_to_go == 0:               #check to see if the grid is completed
            self.is_user_done = True
        else:
            self.is_user_done = False

    #compare the users answers to the solution and see if they mach
    #if not add the location of the error to the lest
    def get_wrong_locations(self):
        self.wrong_locations = []
        for i in xrange(len(self.answer_string)):
            if self.answer_string[i] <> self.solution_string[i] and self.answer_string[i] <> '0':
                    self.wrong_locations.append(i)
        self.number_wrong = len(self.wrong_locations)

    #compare the users answers to the solution and see if they mach
    #if they do add the location of the answer to the lest
    def get_correct_locations(self):
        self.correct_locations = []
        for i in xrange(len(self.answer_string)):
            if self.answer_string[i] == self.solution_string[i] and self.grid_string[i] == '0':
                self.correct_locations.append(i)
        self.number_correct = len(self.correct_locations)

    #count how many cells have no value
    def count_blanks(self):
        self.number_blank = 0
        for i in xrange(len(self.answer_string)):
            if self.answer_string[i] == '0':
                self.number_blank += 1

    #change the value of the cell to the wrong aswer and the color of the font
    def change_html_for_wrong_answers(self):
        for location in self.wrong_locations:            
            coord = self.convert_string_to_coord(location)
            self.html.grid['id'][int(coord[0])][int(coord[1])] = 'wrong_cell'
            self.html.grid['value'][int(coord[0])][int(coord[1])] = self.answer_string[location]

    #change the value of the cell to the correctr answer
    def change_html_for_right_answers(self):
        for location in self.correct_locations:
            coord = self.convert_string_to_coord(location)
            self.html.grid['value'][int(coord[0])][int(coord[1])] = self.answer_string[location]

    #convert the location in the string to a coord on the grid
    def convert_string_to_coord(self, location):
        i = str(int(location)/9)
        j = str(int(location)%9)
        return i+j

    #remove all the of the users answers and render the original puzzle
    def clear_board(self):
        self.grid = board.BoardManipulations().make_grid(self.grid_string)
        self.html = SudokuHtml(self.grid)

    #show the user the solution
    def solve_board(self):
        self.grid = board.BoardManipulations().make_grid(self.solution_string)
        self.html = SudokuHtml(self.grid)

    #convert the elapsed time to a string
    def completetion_time(self):
        t = int(time.time()-self.start_time)
        self.time_in_seconds = t
        hours = t/3600
        t -= hours*360
        minutes = t/60
        self.time = minutes
        seconds = t - minutes*60
        self.time = ''
        if hours > 0 :
            self.time += str(hours) + ' hour'
            if hours > 1:
                self.time += 's'
            self.time += ' '
        if minutes > 0:
            self.time += str(minutes) + ' minute'
            if minutes > 1:
                self.time += 's'
            self.time += ' '
        if self.time <> '':
            self.time += 'and '
        self.time += str(seconds) + ' second'
        if seconds <> 1:
            self.time += 's'

    #add a congratulation
    def make_congratulations(self):
        self.congratulations = 'Congratulations you solved the puzzle in '
        self.congratulations += self.time