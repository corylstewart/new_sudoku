function enter_puzzle_as_string() {
    clear_blank_board()
    var puzzle_string = window.prompt('Enter puzzle a a string with unknowns replace with a zero', '300000080700003052502708000000025070080430000000007090000000006430056007200000300')
    if (puzzle_string.length == 81)
    {
        for (var i = 0; i < 9; i++)
        {
            for (var j = 0; j < 9; j++)
            {
                var cell_name = 'in' + i.toString() + j.toString()
                var cell_value = puzzle_string.substring((i * 9) + j, (i * 9) + j+1)
                if (cell_value == '0'){
                    cell_value = ''
                }
                document.getElementById(cell_name).value = cell_value
            }
        }
    }
}

function clear_board() {
    make_greeting()
    for (var i = 0; i < 9; i++){
        for (var j = 0; j < 9; j++){
            var cell_name = 'in' + i.toString() + j.toString()
            var this_cell = document.getElementById(cell_name)
            if (!this_cell.readOnly) {
                this_cell.value = ''
                this_cell.className = 'emptycell'
            }
        }
    }
}

function clear_blank_board() {
    make_new_user_grid()
    for (var i = 0; i < 9; i++) {
        for (var j = 0; j < 9; j++) {
            var cell_name = 'in' + i.toString() + j.toString()
            var this_cell = document.getElementById(cell_name)
            this_cell.value = ''
            this_cell.className = 'emptycell'
            this_cell.readOnly = false
            this_cell.onBlur = 'j8(this)'
            this_cell.maxLength = 1
        }
    }
}

function solve_puzzle() {
    var puzzle_string = ''
    for (var i = 0; i < 9; i++) {
        for (var j = 0; j < 9; j++) {
            var cell_name = 'in' + i.toString() + j.toString()
            var cell_value = document.getElementById(cell_name).value
            if (cell_value == '') {
                cell_value = '0'
            }
            puzzle_string += cell_value
        }
    }
    document.getElementById('user_puzzle_input_id').value = puzzle_string
    document.getElementById('user_puzzle_form').submit()
}

function show_errors() {
    check_progress()
    document.getElementById('user_puzzle_input_id').value = puzzle_solution.toString()
    for (var i = 0; i < 9; i++) {
        for (var j = 0; j < 9; j++) {
            var cell_name = 'in' + i.toString() + j.toString()
            var loc = (i * 9) + j
            var this_cell = document.getElementById(cell_name)
            if (this_cell.className != 'full_cell' && this_cell.value != '') {
                if ( this_cell.value == puzzle_solution.substring(loc,loc+1)) {
                    this_cell.className = 'emptycell'
                }
                else {
                    this_cell.className = 'wrongcell'
                }
            }
        }
    }
}

function check_progress() {
    document.getElementById('user_puzzle_input_id').value = puzzle_solution.toString()
    var count = 0
    var zeros = 0
    for (var i = 0; i < 9; i++) {
        for (var j = 0; j < 9; j++) {
            var cell_name = 'in' + i.toString() + j.toString()
            var loc = (i * 9) + j
            var this_cell = document.getElementById(cell_name)
            if (this_cell.className != 'full_cell' && this_cell.value != '') {
                this_cell.className = 'emptycell'
                if (this_cell.value != puzzle_solution.substring(loc, loc + 1)) {
                    count++
                }
            }
            if (this_cell.className != 'full_cell' && this_cell.value == '') {
                zeros++
            }
        }
    }
    var new_content = ''
    zeros += count
    if (zeros == 0 && count == 0) {
        new_content += 'Congratulations you have solved the puzzle!'
    }
    
    else if (count == 0) {
        new_content += 'You have made no errors yet'
    }
    else if (count == 1) {
        var new_content = 'You have made one error'

    }
    else {
        var new_content = 'You have made ' + count.toString() + ' errors.'       
    }
    if (zeros == 1) {
        new_content += ', and still have one square to fill in correctly.'
    }
    else if (zeros > 1) {
        new_content += ' and still have ' + zeros.toString() + ' squares to fill in correctly.'
    }
    edit_greeting_span(new_content)
}


function show_solution() {
    for (var i = 0; i < 9; i++) {
        for (var j = 0; j < 9; j++) {
            var cell_name = 'in' + i.toString() + j.toString()
            var loc = (i * 9) + j
            var this_cell = document.getElementById(cell_name)
            if (this_cell.className != 'full_cell') {
                this_cell.className = 'emptycell'
                this_cell.value = puzzle_solution.substring(loc, loc+1)
            }
        }
    }
}

function get_new_puzzle() {
    window.location.href = document.URL
}

function edit_greeting_span(new_content) {
    var span = document.getElementById('progress_message')
    while (span.firstChild){
            span.removeChild( span.firstChild );
    }
    span.appendChild( document.createTextNode(new_content) );
}

function make_greeting() {
    edit_greeting_span('Here is the puzzle. Good luck')
}

function make_new_user_grid() {
    edit_greeting_span('Please enter you puzzle below.')
}

function remove_space(cur) {
    if (cur.value == ' ') {
        cur.value = ''
    }
}