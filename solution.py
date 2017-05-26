assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    def eliminate_twins(values, units):
        for row in units:
            values_reversed = {}
            rows = dict(filter(lambda entry: len(entry[1]) > 1 and entry[0] in row, values.items()))
            if len(rows) < 3:
                continue
            for position, value in rows.items():
                if value in values_reversed:
                    values_reversed[value] |= set([position])
                else:
                    values_reversed[value] = set([position])
            for twins_value, twins in filter(lambda entry: len(entry[0]) == 2 and len(entry[1]) == 2, values_reversed.items()):
                for position, value in filter(lambda entry: entry[0] not in twins, rows.items()):
                    values[position] = ''.join(sorted(set(value) - set(twins_value)))
        return values
    
    values = eliminate_twins(values, row_units)
    values = eliminate_twins(values, column_units)
    values = eliminate_twins(values, square_units)
    values = eliminate_twins(values, diagonal_units)

    return values

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return {cell: value if value is not '.' else '123456789' for (cell, value) in zip(boxes, grid)}

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    print('   {}'.format(''.join([c.center(width) + ('|' if c in '36' else '') for c in cols])))
    print('   {}'.format(line))
    for r in rows:
        print('{}| {}'.format(r, ''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols)))
        if r in 'CF': print('   {}'.format(line))
    return

def eliminate(values):
    known_values = {position: value for position, value in values.items() if len(value) == 1}
    for position, value in known_values.items():
        for peer in peers[position]:
            values[peer] = values[peer].replace(value, '')
    return values

def only_choice(values):
    def possible_values_for_peers(position, set_of_peers):
        """Gather all the values for all pears in a row, column or square (depending which set_of_peers do you pass as a parameter)"""
        possible_values = set()
        for peer_positions in filter(lambda peers: position in peers, set_of_peers):
            peer_positions = list(filter(lambda peer: peer != position, peer_positions))
            for value in map(lambda cell: values[cell], peer_positions):
                possible_values |= set(value)
        return possible_values

    for position, value in values.items():
        if len(value) > 1:
            value_set = set(value)
            
            possible_values = possible_values_for_peers(position, square_units)
            diff = value_set - possible_values
            if len(diff) == 1:
                values[position] = diff.pop()
                continue

            possible_values = possible_values_for_peers(position, row_units)
            diff = value_set - possible_values
            if len(diff) == 1:
                values[position] = diff.pop()
                continue

            possible_values = possible_values_for_peers(position, column_units)
            diff = value_set - possible_values
            if len(diff) == 1:
                values[position] = diff.pop()
                break

            possible_values = possible_values_for_peers(position, diagonal_units)
            diff = value_set - possible_values
            if len(diff) == 1:
                values[position] = diff.pop()
                break
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if values is False:
        return False

    if max(map(len, values.values())) == 1:
        for diagonal in diagonal_units:
            inverted_values = {}
            for position, value in filter(lambda entry: entry[0] in diagonal, values.items()):
                inverted_values[value] = inverted_values.get(value, [])
                inverted_values[value].append(position)
            if max(map(len, inverted_values.values())) > 1:
                return False
        return values
    
    # Choose one of the unfilled squares with the fewest possibilities
    unsolved_values = {key: value for key, value in values.items() if len(value) > 1}
    fewest_cell_position, fewest_cell_value = min(unsolved_values.items(), key = lambda entry: len(entry[1]))
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for possible_value in fewest_cell_value:
        possible_values = values.copy()
        possible_values[fewest_cell_position] = possible_value
        solution = search(possible_values)
        if solution is not False:
            return solution
        
    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = eliminate(values)
    values = naked_twins(values)
    values = search(values)
    return values

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)
boxes = [
    'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9',
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9',
    'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
    'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9',
    'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9',
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9',
    'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9',
    'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9',
    'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9'
]

row_units = [cross(r, cols) for r in rows]
# Element example:
# row_units[0] = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
# This is the top most row.

column_units = [cross(rows, c) for c in cols]
# Element example:
# column_units[0] = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1']
# This is the left most column.

square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Element example:
# square_units[0] = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
# This is the top left square.

diagonal_units = [[row + col for row, col in zip(rows, cols)], [row + col for row, col in zip(rows, reversed(cols))]]

unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

if __name__ == '__main__':
    # display(solve('..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'))

    # display(solve(
    #     '1.4.9..68' +
    #     '956.18.34' +
    #     '..84.6951' +
    #     '51.....86' +
    #     '8..6...12' +
    #     '64..8..97' +
    #     '781923645' +
    #     '495.6.823' +
    #     '.6.854179'
    # ))

    display(solve('2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'))

    # diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
