from EnhancedHandler import EnhancedHandler as EH

def make_cell_type(puzzle,i,j):
		    cell_value = puzzle[(i*8)+j]
		    if cell_value <> '0':
		        return 'readonly value='+cell_value
		    else:
		        return 'maxlength=1 onblur=j8(this)'
		
def make_td_class(i,j):
    td_class = 'class='
    if i in [0,3,6]:
        td_class += 'top'
    else:
        td_class += 'mid'
    if j in [0,3,6]:
        td_class += 'left'
    else:
        td_class += 'midl'
    return td_class

def make_input_class(puzzle,i,j):
    cell_value = puzzle[(i*8)+j]
    if cell_value == '0':
        return 'emptycell'
    else:
        return 'full_cell'



class SudokuUserGeneratedHnadler(EH.EnhancedHandler):
	pass
	
	

class SudokuHandler(EH.EnhancedHandler):
    def get(self):
        self.arg_dict['name'] = 'Cory'
        self.arg_dict['puzzle_solution'] = '164895273273614598958732146839526417647189352512473689485267931796341825321958764'
        mask = '111011110010011110101110110110110001111111111100011011011011101011110010011110111'        
        self.arg_dict['puzzle'] = ''
        for i in range(len(mask)):
            if mask[i] == '0':
                self.arg_dict['puzzle'] += '0'
            else:
                self.arg_dict['puzzle'] += self.arg_dict['puzzle_solution'][i]
        for i in range(9):
            for j in range(9):
                self.arg_dict['celltype'+str(i)+str(j)] = make_cell_type(self.arg_dict['puzzle'],i,j)
                self.arg_dict['ca'+str(i)+str(j)] = make_td_class(i,j)
                self.arg_dict['cb'+str(i)+str(j)] = make_input_class(self.arg_dict['puzzle'],i,j)
        #self.write(self.arg_dict)
        self.render('Newer Sudoku.html', **self.arg_dict)



		