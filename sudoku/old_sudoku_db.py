import random

from google.appengine.ext import ndb

#create the Sudoku Puzzle class for the database
class Sudoku(ndb.Model):
    grid = ndb.StringProperty()
    solution = ndb.StringProperty()
    level = ndb.IntegerProperty()
    user = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now = True)
    rand = ndb.FloatProperty()

    #return a random puzzle of a certain level from the DB
    def get_puzzle(self, level):
        puzzles = Sudoku.query(Sudoku.level == level)
        puzzle = random.randint(1,puzzles.count())
        i = 0
        for p in puzzles:
            i+=1
            if i == puzzle:
                return p

    #much more efficient
    def get_random_puzzle(self, level):
        rand = random.random()              #sets a random float
        puzzle = Sudoku.query(Sudoku.level == level, Sudoku.rand > rand).fetch(limit = 1)   #get first puzzle with rand higher
        for p in puzzle:                                                                    #than the random float
            p.rand = random.random()                #set a new value for rand
            p.put()                                 #helps to smooth results
            return p                                #return puzzle
    
    #put a new puzzle in the database
    def put_puzzle(self, grid, solution, level, user):
        exists = Sudoku.query(Sudoku.grid == grid)
        if exists.count() == 0:
            sudoku = Sudoku(grid = grid,
                            solution = solution,
                            level = level,
                            user = user,
                            rand = random.random())
            sudoku.put()

    #delete random puzzles from the database
    def delete_sudoku_db(self, limit = 500):
        to_delete = Sudoku.query().fetch(limit = limit)
        for puzzle in to_delete:
            puzzle.key.delete()

    def change_puzzle_rand_to_one(self, level):
        puzzle = self.get_puzzle(level)
        puzzle.rand = 1.0
        puzzle.put()


#read puzzle from a file and place them im the DB
class SudokuFile:
    def put_file_in_db(self, filename = 'sudoku.txt'):
        user = 'base'
        f = open(filename, 'r')
        for line in f:
            puzzle = line.split()
            solution = puzzle[0]
            grid = puzzle[1]
            level = int(puzzle[2])
            add_to_db = Sudoku().put_puzzle(grid, solution, level, user)

    
