import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.variables = list() 
        self.domains = dict() # dict of lists
        self.neighbours = dict() # dict of lists
        self.removedlist = dict() # dict of lists of tuples
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.setup(puzzle)

    def setup(self, puzzle):
        for i in range(9):
            for j in range(9):
                key = str(i) + str(j)
                self.variables.append(key)

                if puzzle[i][j] == 0:
                    self.domains[key] = list(range(1,10))
                    self.removedlist[key] = list()
                else:
                    self.domains[key] = [puzzle[i][j]]


                self.neighbours[key] = list()
                for k in range(9):
                    if k != j:
                        self.neighbours[key].append(str(i) + str(k))
                for h in range(9):
                    if h != i:
                        self.neighbours[key].append(str(h) + str(j))

                pos_x = i // 3;
                pos_y = j // 3;
                for x in range(pos_x * 3, pos_x * 3 + 3):
                    for y in range(pos_y * 3, pos_y * 3 + 3):
                        v = str(x) + str(y)
                        if x != i and y != j:
                            if (v not in self.neighbours[key]):
                                self.neighbours[key].append(v)




    def solve(self):
        # TODO: Write your code here
        
        if self.preprocess():

            if not self.is_solved():
                assignment = dict()

                #initialise assignment
                for variable in self.variables:
                    if len(self.domains[variable]) == 1:
                        assignment[variable] = self.domains[variable][0]

                assignment = self.backtrack(assignment)
                
                for var in self.domains:
                    self.domains[var] = assignment[var]
        else:
            raise ValueError("Failed")
        count = 0
        for i in range(9):
            for j in range(9):
                
                val = self.domains[self.variables[count]]
                self.ans[i][j] = val
                count += 1

        #self.ans = result[i][j]
        # self.ans is a list of lists
        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

    def preprocess(self):
        constraint_queue = list()
        for v in self.variables:
            for neighbour in self.neighbours[v]:
                constraint_queue.append((v, neighbour))

        while len(constraint_queue) != 0:
            arc = constraint_queue.pop(0)
            if self.revise(arc[0], arc[1]):
                if len(self.domains[arc[0]]) == 0:
                    return False
                for n in self.neighbours[arc[0]]:
                    if n != arc[1] and (arc[0], n) not in constraint_queue:
                        constraint_queue.append((arc[0], n))
        return True

    def revise(self, v1, v2):
        revised = False
        for d1 in self.domains[v1]:
            if len(self.domains[v2]) == 1 and d1 in self.domains[v2]:
                self.domains[v1].remove(d1)
                revised = True
        return revised 

    def is_solved(self):
        solved = True
        for v in self.variables:
            if len(self.domains[v]) != 1:
                solved = False
        return solved

    
    #checks if a value assigned is valid
    def isValid(self, assignment, var, val):
        for variable in assignment:
            if variable in self.neighbours[var] and assignment[variable] == val:
                return False
        return True


    #Select using most constrained variable heuristic
    def select_unassigned_variable(self, assignment):
        leastValues = 10
        for var in self.variables:
            if var not in assignment:
                if len(self.domains[var]) < leastValues:
                    leastValues = len(self.domains[var])
                    current = var;
        return current

    #Select the least constraining value
    def order_domain_values(self, var):
        if len(self.domains[var]) == 1:
            return self.domains[var]
        return sorted(self.domains[var], key = lambda val: self.no_of_conflicts(var, val))

    def no_of_conflicts(self, var, val):
        count = 0

        for v in self.neighbours[var]:
            if len(self.domains[v]) > 1 and val in self.domains[v]:
                count += 1

        return count

    #Backtracking search algorithm
    def backtrack(self, assignment):
        if len(assignment) == len(self.variables):
            return assignment

        variable = self.select_unassigned_variable(assignment)

        for val in self.order_domain_values(variable):
            if self.isValid(assignment, variable, val):

                self.assign(assignment, variable, val)
                result = self.backtrack(assignment)
                if result:
                    return result
            self.unassign(assignment, variable)

        return False

    def assign(self, assignment, var, val):
        assignment[var] = val
        #self.domains[var] = [val]

        self.forwardcheck(assignment, var, val)

    def unassign(self, assignment, var):
        if var in assignment:
            for (neighbour, val) in self.removedlist[var]:
                self.domains[neighbour].append(val)

            self.removedlist[var] = []

            del assignment[var]

    def forwardcheck(self, assignment, var, val):
        for neighbour in self.neighbours[var]:
            if neighbour not in assignment:
                if val in self.domains[neighbour]:
                    self.domains[neighbour].remove(val)
                    self.removedlist[var].append((neighbour, val))


if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
