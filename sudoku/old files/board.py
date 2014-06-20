#import grids
import copy
import time

class BoardManipulations:
    'Manipulates the board by switch rows, columns and squares'

    #switch the columns and the rows so that
    #the solver can be applied by on a row
    def make_rows(self):
        new_grid = []
        for i in xrange(9):
            new_grid.append([])
            for j in xrange(9):
                new_grid[i].append(self.board[j][i])
        self.board = new_grid

    #switch the squares and the rows so that
    #the solver can be applied by on a row
    def make_squares(self):
        square = []
        squares = []
        for y in xrange(0,3):
            for z in xrange(0,3):
                for i in xrange(0,3):
                    for j in xrange(0,3):
                        square.append(self.board[(i+(y*3))][(j+(z*3))])
                squares.append(square)
                square = []
        self.board = squares

    #removes zeros from the board a places a list of number 1-9
    def place_lists(self):
        for i in xrange(9):
            for j in xrange(9):
                if self.board[i][j] == 0:
                    self.board[i][j] = [x for x in xrange(1,10)]

    #removes any lists from the board and replaces them with a zero
    def remove_lists(self):
        for i in xrange(9):
            for j in xrange(9):
                if type(self.board[i][j]) == type([]):
                    self.board[i][j] = 0

    #create a blank grid
    def blank_grid(self):
        return [[0 for j in xrange(9)] for i in xrange(9)]

    #convert the grid string to a grid
    def make_grid(self, grid_string):
        grid = [[[] for j in xrange(9)] for i in xrange(9)]
        for i in xrange(9):
            for j in xrange(9):
                grid[i][j] = int(grid_string[:1])
                grid_string = grid_string[1:]
        return grid

    #convert a grid to a grid string
    def make_grid_string(self, grid):
        grid_string = ''
        for i in xrange(9):
            for j in xrange(9):
                grid_string = grid_string + str(grid[i][j])
        return grid_string



class BoardStatus(BoardManipulations):
    'Checks status of the board.  Checks for valid and finished boards'

    #Checks to see if a board is valid
    def check_valid(self):
        if len(self.board) <> 9:    #make sure there are 9 rows
            return False
        for row in self.board:      #make sure each row has 9 columns
            if len(row) <> 9:
                return False
        if self.check_minimum():    #check to see if there are at least 17 knowns
            if self.check_numbers():    #make sure there are no repeats in each row
                self.make_rows()
                if self.check_numbers():    #make sure there are no repeats in each column
                    self.make_rows()
                    self.make_squares()
                    if self.check_numbers():    #make sure there are no repeats in each square
                        self.make_squares()
                        return True             #return true if it passed all of the tests
                    else:
                        self.make_squares()
                else:
                    self.make_rows()
        return False

    #make sure that there are no reapeated number in each row
    def check_numbers(self):
        for row in self.board:
            for number in xrange(1,10):
                if row.count(number) > 1:
                    return False
                for col in row:
                    if type(col) == type([]):
                        if len(col) == 0:
                            return False
        return True

    #make sure there are at least 17 knowns which is the least number
    #of knowns you can have and still have a solvable puzzle
    def check_minimum(self):
        count = 0
        for i in xrange(9):
            for j in xrange(9):
                if type(self.board[i][j]) == type(int()) and self.board[i][j] <> 0:
                    count += 1
        if count < 17: return False
        else: return True

    #check to see that a board is complete and valid
    def check_done(self):
        count = 0
        for row in self.board:
            for col in row:
                if type(col) == type(int()) and col <> 0:
                    count += 1
        if count <> 81: return False
        else: return self.check_valid()

         



class SudokuTechniques(BoardManipulations):
    '''Contains the different techniques that can be applied to a board
    to remove unknown possiblilties and narrow down the board'''

    #remove unkowns for the lists by using knowns within each row
    def remove_numbers(self):
        for row in self.board:
            found = []      #create an empty list for known numbers
            for col in row:
                if type(col) == type(int()):
                    found.append(col)      #append the known list with known numbers
            for number in found:    #for each known remove the known from each
                for col in row:     #list of unknowns
                    if type(col) == type([]):
                        if number in col:
                            col.remove(number)
        self.remove_single_lists()  #check to see if unknowns are now known
        self.remove_lonely()        #check to see all of the unkowns contain exactly one number

    #check if the lenght of a unknown is exactly one and make it a known
    def remove_single_lists(self):
        for i in xrange(9):
            for j in xrange(9):
                if type(self.board[i][j]) == type([]):
                    if len(self.board[i][j]) == 1:
                        self.board[i][j] = self.board[i][j][0]

    #check to see if a number is known because it occurs only once
    def remove_lonely(self):
        for i in xrange(9):
            numbers = []    #create a empty list for a total count of numbers
            list_of_lists = [x for x in self.board[i] if type(x) == type([])]   #create a list of all of the unknown lists
            for list in list_of_lists:  #break the lists down and append the numbers list with all of the numbers
                for number in list:     #in each of the lists
                    numbers.append(number)
            for j in xrange(9):
                if type(self.board[i][j]) == type(int()):   #append the numbers list with all of the known numbers
                    numbers.append(self.board[i][j])
            remove = []         #create an empty list for numbers that will be knowns
            for j in xrange(1,10):
                if numbers.count(j) == 1:   #if the number occers only once in the grid append the remove list
                    remove.append(j)
            for number in remove:   #the numbers in the remove list are now knowns
                for j in xrange(9): #and can be placed as knowns in the board
                    if type(self.board[i][j]) == type([]):  #find the unknown list that contains the known number
                        if number in self.board[i][j]:      #set the unknown list to a known number
                            self.board[i][j] = number

    #look for sets of pairs, triplets, and quads and take those sets out of other unknown lists
    def remove_sets(self):
        for k in xrange(2,5):
            for i in xrange(9):
                found = []
                for j in xrange(9):
                    #if the unkown is of length k and has a k-1 matches it is a set and can be added to the found list
                    if type(self.board[i][j]) == type([]) and len(self.board[i][j]) == k and \
                                self.board[i].count(self.board[i][j]) == k and self.board[i][j] not in found:
                        found.append(self.board[i][j])
                #for the sets found the members of the set can be removed from any other list of unkowns
                for list in found:
                    for number in list:
                        for j in xrange(9):
                            #if the unkown list is not member of the set but, contains a member of the set can be
                            #removed from that list
                            if type(self.board[i][j]) == type([]) and self.board[i][j] <> list and \
                                        number in self.board[i][j]:
                                self.board[i][j].remove(number)

    #Look for the hidden pairs of a board.  A hidden pair is a set of pairs who have other unknowns making
    #the fact that they are actually a member of a pair
    def remove_hidden_pairs(self):
        for i in xrange(9):
            count = {}  #create a dictionary that will keep count of occurances of unkowns
            for j in xrange(9):
                if type(self.board[i][j]) == type([]):  #find a list of unknown
                    for number in xrange(1,10):     #cycle through number 1-9
                        if number in self.board[i][j]:  #if a number is found add it to the count of that number
                            if number not in count:
                                count[number] = [0,[]]
                            count[number][0] = count[number][0] + 1 #add to the count
                            count[number][1].append(j)              #add the location of the number
            for key1 in count:      #cycle through the dictionary for key1
                for key2 in count:  #cycle through the dictionary for key2
                    #if key1 and key 2 are different,both have a count of 2 and 
                    #share the same locations they are a hidden pair
                    if key1 <> key2 and count[key1] == count[key2] and count[key1][0] == 2:
                        #set the new value of the unkown to the values of key1 and key2
                        for col in count[key1][1]:
                            self.board[i][col] = [key1, key2]
            #sort the unkowns so that the are in numeric order
            for j in xrange(9):
                if type(self.board[i][j]) == type([]):
                    self.board[i][j].sort()




class SudokuSolver(SudokuTechniques):
    'Applies the different technoques to solve the puzzle and assign a difficulty to the board'

    #print the board so that it is easier to look at
    def print_grid(self):
        for row in self.board:
            print row
        print'---------------------------------------'

    #Level one only applies the removal of numbers based on knowns
    def level_one(self):
        old_grid = []
        while old_grid <> self.board:
            old_grid = copy.deepcopy(self.board)
            self.remove_numbers()
            self.make_rows()
            self.remove_numbers()            
            self.make_rows()
            self.make_squares()
            self.remove_numbers()            
            self.make_squares()
        self.done = self.check_done()

    #level two applies the technique of set removal and level one
    def level_two(self):
        old_grid = []
        while old_grid <> self.board:
            old_grid = copy.deepcopy(self.board)
            self.remove_sets()
            self.make_rows()
            self.remove_sets()
            self.make_rows()
            self.make_squares()
            self.remove_sets()
            self.make_squares()
            self.level_one()
        self.done = self.check_done()

    #level thee applies the technique of hidden pairs and level two
    def level_three(self):
        old_grid = []
        while old_grid <> self.board:
            old_grid = copy.deepcopy(self.board)
            self.remove_hidden_pairs()
            self.make_rows()
            self.remove_hidden_pairs()
            self.make_rows()
            self.make_squares()
            self.remove_hidden_pairs()
            self.make_squares()
            self.level_two()
        self.done = self.check_done()

    #if a grid is still not done apply a brute force solver
    def brute_force(self):
        possible = []   #list of possible grids byt setting one unknown to a possible number
        solutions = []  #list of solutions just in case there is more than one solution
        for i in range(9):
            for j in range(9):
                if type(self.board[i][j]) == type([]):      #for each list of unkowns place a possible number
                    for number in self.board[i][j]:         #in that location and append the list of possible with
                        grid = copy.deepcopy(self.board)    #that board
                        grid[i][j] = number
                        possible.append(copy.deepcopy(grid))
        for grid in possible:                               #for each possible grid send it to the solver
            try_it = Board(grid = grid, use_bf = False)
            if try_it.done == True:
                if try_it.board not in solutions:
                    solutions.append(try_it.board)          #if a solution is found add it to the list of solutions
        self.solutions = solutions

    #run the board though the differnt solver levels
    def solve_sudoku(self):
            start = time.time()
            if self.valid:              #check that the list is valid
                self.place_lists()
                self.level_one()        #apply level one
                if self.done == True:
                    self.level = 1
                    self.time = time.time() - start
                    return
                self.level_two()        #apply level two
                if self.done == True:
                    self.level = 2
                    self.time = time.time() - start
                    return
                self.level_three()
                if self.done == True:   #apply level three
                    self.level = 3
                    self.time = time.time() - start
                    return
                if self.use_bf == True: #if the board is not solved and use brute force
                    self.level = 10     #is true apply the brute force solution
                    self.brute_force()
                    self.time = time.time() - start
                    if len(self.solutions) > 1:         #if multiple solutions set the first as a solution
                        self.board = self.solutions[0]                    
                    if len(self.solutions) == 1:        #if there is exactly one solution set the board value
                        self.board = self.solutions[0]  #to that solutions
                        self.done = True
                        self.solutions = []             #reset the solutions to a blank list
  
class Board(BoardStatus, SudokuSolver):
    'Define the sudoku board'

    def __init__(self, grid_string = '', grid = '', use_bf = True):
        self.grid_string = grid_string
        if grid <> '':          #if the board is a grid
            self.board = grid   #set the board to the value of the grid
            self.grid_string = self.make_grid_string(grid)  #create a grid_string for that grid
        elif grid_string == '':     #if the both the grid and grid_string are empty make a blank board
            self.board = self.blank_grid()

        elif len(grid_string) <> 81:    #if the grid_string is not of lenth 81 make a blank board
            self.board = self.blank_grid()
        else:
            self.board = self.make_grid(grid_string)    #make the board out of the value of the grid_string

        self.grid = copy.deepcopy(self.board)           #set the value of the grid to that of the board
        self.valid = self.check_valid()                 #check if the board is valid
        self.done = self.check_done()                   #check if the board is done
        self.level = 0                                  #set the initial level to 0
        self.time = 0                                   #set the solution time to 0
        self.solution = self.blank_grid()               #set the solution to a blank grid
        self.solution_string = '0'*81                   #set the solution string to zeros
        self.solutions = []                             #set the solutions list to blank list
        self.use_bf = use_bf                            #set the value of use brute force to True/False default is true
        self.solve_sudoku()                             #solve the grid

        if self.done == True:
            self.solution = self.board
            self.solution_string = self.make_grid_string(self.solution)
        elif len(self.solutions) > 1:
            self.solution = self.solutions[0]
            self.solution_string = self.make_grid_string(self.solution)
        else:
            self.remove_lists()
            self.solution = self.board


class CreateNewPuzzle:
    
    #This is a valid full grid for use in creating new puzzles
    base_grid = [[1,7,4,2,8,5,3,9,6],
                      [3,9,6,4,1,7,5,2,8],
                      [8,5,2,9,6,3,1,7,4],
                      [4,1,7,5,2,8,6,3,9],
                      [6,3,9,7,4,1,8,5,2],
                      [2,8,5,3,9,6,4,1,7],
                      [7,4,1,8,5,2,9,6,3],
                      [9,6,3,1,7,4,2,8,5],
                      [5,2,8,6,3,9,7,4,1]]


word = Board(grid_string='000000000530602000001350007109000070007900030000000009060010054000430006300007000')
#word = Board(grid=grids.hardest_ever)
#word = Board()
print word.solution
print word.level
print word.time


