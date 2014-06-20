from SuperHandler import SuperHandler as SH
import sudoku_db as sdb
import sudoku_html as shtml
import board
import time

class SudokuHandlerUserGenerated(SH.SuperHandler):
    def get(self):
        self.arg_dict['grid'] = shtml.SudokuHtml().grid     #create a empty grid
        self.render('sudoku.html', **self.arg_dict)

    def post(self):
        solve = self.request.get('solve_btn')
        clear = self.request.get('clear_btn')

        if solve:
            user_grid = shtml.UserGrid(self)        #solve the user grid
            self.arg_dict['grid'] = user_grid.grid.grid     #add the html to the argument dictionary
            self.arg_dict['difficulty'] = user_grid.user_solution.level
            if user_grid.user_solution.valid == False:      #if the puzzle is not valid show error to user
                self.arg_dict['error'] = 'Sorry that is not a valid puzzle'            
            if user_grid.user_solution.done == False:       
                if len(user_grid.user_solution.solutions) > 0: #if there are multiple solutions show the first one
                    self.arg_dict['error'] = 'Sorry there are multile \
                                             solutions to your puzzle.  Here is one.'
                    self.arg_dict['grid'] = user_grid.grid.grid
                else:               #if no solution was found show the current state of the puzzle
                    self.arg_dict['error'] = 'Your puzzle was too hard for me I could \
                                                not find a solution.  This is as far as I got.'
            else:       #if the puzzle was solved place it into the database
                sdb.Sudoku().put_puzzle(user_grid.user_grid_string,user_grid.user_solution.solution_string, 
                                        user_grid.user_solution.level, self.user)
            self.render('sudoku.html', **self.arg_dict)


        if clear:
            self.redirect('/sudoku')

class SudokuHandlerLevels(SH.SuperHandler):
    def get(self):
        self.level = int(self.request.get('level'))
        self.arg_dict['level'] = self.level         #set the level
        self.start_time = time.time()
        self.arg_dict['start_time'] = self.start_time   #set the start time
        puzzle = shtml.RandomPuzzle(self.arg_dict['level']) #get a random puzzle
        self.arg_dict['grid_string'] = puzzle.grid_string   #set the grid string
        self.arg_dict['solution_string'] = puzzle.solution_string   #set the solution string
        self.arg_dict['grid'] = puzzle.html.grid        #set the grid html
        self.render('sudoku.html', **self.arg_dict)

    def post(self):
        check = self.request.get('check_btn')
        clear = self.request.get('clear_btn')
        solve = self.request.get('solve_btn')
        new_puzzle = self.request.get('new_btn')
        check_user = shtml.CheckUser(self)
        

        if check:
            check_user.check_user()     #check the users answers versus the solution
            self.arg_dict['grid_string'] = check_user.grid_string
            self.arg_dict['solution_string'] = check_user.solution_string
            self.arg_dict['grid'] = check_user.html.grid
            self.arg_dict['level'] = check_user.level
            self.arg_dict['start_time'] = check_user.start_time
            self.arg_dict['wrong'] = check_user.number_wrong
            self.arg_dict['missing']  = check_user.cells_to_go
            if check_user.is_user_done:     #if the user is done congratulate them
                self.arg_dict['congratulations'] = check_user.congratulations
                #add user to DB at some point for all puzzles finished

        if clear:
            self.start_time = time.time()   #reset the start time for the user
            check_user.clear_board()        #clears all user numbers from the grid
            self.arg_dict['grid_string'] = check_user.grid_string
            self.arg_dict['solution_string'] = check_user.solution_string
            self.arg_dict['grid'] = check_user.html.grid
            self.arg_dict['level'] = check_user.level
            self.arg_dict['start_time'] = self.start_time


        if solve:
            self.start_time = time.time()
            check_user.solve_board()        #show the user the solution to the puzzle
            self.arg_dict['grid_string'] = check_user.grid_string
            self.arg_dict['solution_string'] = check_user.solution_string
            self.arg_dict['grid'] = check_user.html.grid
            self.arg_dict['level'] = check_user.level
            self.arg_dict['start_time'] = self.start_time
            

        if new_puzzle:
            #get a new puzzle 3for the user
            self.level = self.request.get('level')
            self.redirect('/sudoku/levels?level='+self.level)
            return
         
        #render the template   
        self.render('sudoku.html', **self.arg_dict)

        

class SudokuDBHandler(SH.SuperHandler):
    def get(self):
        if self.check_admin():
            self.render('sudoku-db.html', **self.arg_dict)

    def post(self):
        make_db_btn = self.request.get('make_db_btn')
        delete_db_btn = self.request.get('delete_db_btn')
        place_ones_btn = self.request.get('place_ones_btn')
        random_old = self.request.get('random_old')
        random_new = self.request.get('random_new')

        if make_db_btn:     #retieve the file of puzzles and add them to the db
            sdb.SudokuFile().put_file_in_db()
            self.write('done')

        if delete_db_btn:       #deletes a number of random puzzle from the DB
            sdb.Sudoku().delete_sudoku_db()
            self.write('done')

        if place_ones_btn:
            p = sdb.Sudoku()
            for i in xrange(1,4):
                p.change_puzzle_rand_to_one(i)
            self.write('done')

        if random_old:
            start = time.time()
            p = sdb.Sudoku().get_puzzle(1)
            self.write(p)
            self.write('<br>')
            self.write(time.time()-start)

        if random_new:
            start = time.time()
            p = sdb.Sudoku().get_random_puzzle(1)
            self.write(p)
            self.write('<br>')
            self.write(time.time()-start)