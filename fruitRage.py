from sys import maxint
from string import ascii_uppercase
from time import clock


def MAX_VALUE(current, a, b):
    '''Return the minimax value of current state.

    Args:
        current : current node (maximizing entity)
        a : alpha value
        b : beta value
    '''

    # Base case - stop expanding tree if all fruits are taken or if tree is expanded till chosen depth_limit
    if current.fruitsRemaining == 0 or current.depth == depth_limit:
        return current.max_score + current.min_score

    global optimal

    # Sorting child nodes to increase pruning at the root level in a deeper tree, and bigger board (n > 5)
    if current.depth == 0 and depth_limit >= 3 and n > 5:

        # print "sorting max...................", current.depth
        successorsList = current.get_successors()
        # sort the list of successor nodes in descending order of tmp value
        successorsList.sort(key=lambda x: x.tmp, reverse=True)

        # Continue expanding successors (minimizing entities)
        for succNode in successorsList:
            temp = MIN_VALUE(succNode, a, b)
            a = max(a, temp)

            # Update optimal minimax value obtained at root level
            if current.depth == 0:
                if not optimal:
                    optimal = (temp, succNode.move, succNode.matrix)
                elif temp > optimal[0]:
                    optimal = (temp, succNode.move, succNode.matrix)

            # Prune
            if a >= b:
                return b
        return a

    else:
        # Expand successors on-the-go
        for succNode in current.get_successors_generator():
            temp = MIN_VALUE(succNode, a, b)
            a = max(a, temp)
            # Update optimal minimax value obtained at root level
            if current.depth == 0:
                if not optimal:
                    optimal = (temp, succNode.move, succNode.matrix)
                elif temp > optimal[0]:
                    optimal = (temp, succNode.move, succNode.matrix)

            # Prune
            if a >= b:
                return b
        return a


def MIN_VALUE(current, a, b):
    '''Return the minimax value of current state.

    Args:
        current : current node (minimizing entity)
        a : alpha value
        b : beta value
    '''

    # Base case - stop expanding tree if all fruits are taken or if tree is expanded till chosen depth_limit
    if current.fruitsRemaining == 0 or current.depth == depth_limit:
        return current.max_score + current.min_score

    # Sorting child nodes to increase pruning at depth 1
    if (current.depth == 1 and depth_limit >= 5 and n > 6 and n < 16) or \
            (current.depth == 1 and depth_limit >= 3 and n >= 16):

        successorsList = current.get_successors()
        successorsList.sort(key=lambda x: x.tmp, reverse=True)

        for succNode in successorsList:
            temp = MAX_VALUE(succNode, a, b)
            b = min(b, temp)
            # Prune
            if b <= a:
                return a
        return b

    else:
        # Expand successors on-the-go
        for succNode in current.get_successors_generator():
            temp = MAX_VALUE(succNode, a, b)
            b = min(b, temp)
            # Prune
            if b <= a:
                return a
        return b


class node:
    '''Abstract a node in the game playing tree. Define necessary utility methods and generators.'''

    def __init__(self, matrix, depth, fruits):
        '''Construct a game node.'''

        self.matrix = matrix            # The current state (board) of the node
        self.depth = depth              # Depth of the node in the game tree
        self.fruitsRemaining = fruits   # Number of fruits remaining on the board
        self.tmp = 0                    # Number of fruits picked after self.move alone
        self.max_score = 0              # MAX score for sub-tree rooted at this node
        self.min_score = 0              # MIN score for sub-tree rooted at this node
        self.taken = {}
        self.move = None                # Choice of picking a fruit from position (i, j) that created this node

    def pick_fruit_chain(self, row, col, fruit, pos_taken):
        '''Recursively pick all connected fruits of position (row, col) from the board.

        Args:
            row, col : position on board to pick
            fruit : fruit type (0 < fruit <= 9) to pick
            pos_taken : dictionary that tracks positions already visited - helps to ensure creating unique child nodes
        '''

        # Base case - when recursion crosses board boundary
        if row == -1 or col == -1 or row == n or col == n:
            return
        elif self.matrix[row][col] == fruit:
            # Note cell as visited, pick fruit (mark cell as empty), update fruitsRemaining, tmp (fruits picked at node)
            pos_taken[(row, col)] = 1
            self.matrix[row][col] = '*'
            self.fruitsRemaining -= 1
            self.tmp += 1

            # Recurse on connected positions - top, bottom, left, right
            self.pick_fruit_chain(row - 1, col, fruit, pos_taken)
            self.pick_fruit_chain(row + 1, col, fruit, pos_taken)
            self.pick_fruit_chain(row, col - 1, fruit, pos_taken)
            self.pick_fruit_chain(row, col + 1, fruit, pos_taken)

    def enforce_gravity(self):
        '''Apply gravity to make fruits fall down into empty cells below them.'''

        # Gravity is independent in different columns of matrix. So iterating on columns.
        for col in range(n):
            # i marks bottom most cell in col, j checks for fruits above i to fall down
            i = n - 1
            j = i - 1
            while i >= 1:
                # If (i, col) is empty, pull down a fruit from above if any
                if self.matrix[i][col] == '*':
                    while j >= 0:
                        if self.matrix[j][col] != '*':
                            self.matrix[i][col] = self.matrix[j][col]
                            self.matrix[j][col] = '*'
                            # This empty cell filled now, go up to fix more stars
                            i -= 1
                            j -= 1
                            break
                        j -= 1
                    else:
                        # All stars above first star (means entire col is empty), proceed to next col
                        break
                else:
                    # fruit found at (i, col), go up to see if there is a star
                    i -= 1
                    j = i - 1

    def make_move(self, i, j):
        '''Apply move (i,j) on current node. Return resultant new child.'''

        # Deepcopy is terribly slow! Build a child node manually
        newMatrix = []
        for newRow in range(n):
            lst = []
            for newCol in range(n):
                lst.append(self.matrix[newRow][newCol])
            newMatrix.append(lst)

        newNode = node(newMatrix, self.depth + 1, self.fruitsRemaining)
        newNode.max_score = self.max_score
        newNode.min_score = self.min_score

        newNode.move = (i, j)

        # Consume all the connected fruits
        newNode.pick_fruit_chain(i, j, newNode.matrix[i][j], self.taken)

        # Update max_score or min_score based on player turn
        if self.depth % 2 == 0:  # MAX is playing
            newNode.max_score += newNode.tmp ** 2
        else:                   # MIN is playing
            newNode.min_score -= newNode.tmp ** 2

        # Apply gravity after consuming fruits
        newNode.enforce_gravity()

        return newNode

    def get_successors_generator(self):
        '''Yield a child node of the current node.'''

        # Scan the current board bottom to top
        for i in range((n - 1), -1, -1):
            for j in range(n):
                # Good to go if position (i,j) hasn't been considered yet and a fruit exists at (i,j)
                if not self.taken.get((i, j), False) and self.matrix[i][j] != '*':
                    newNode = self.make_move(i, j)
                    newNode.tmp = 0
                    yield newNode
        self.taken = {}

    def get_successors(self):
        '''Return a list of child nodes of the current node.'''

        successors = []

        # Scan the current board bottom to top
        for i in range((n - 1), -1, -1):
            for j in range(n):
                # Good to go if position (i,j) hasn't been considered yet and a fruit exists at (i,j)
                if not self.taken.get((i, j), False) and self.matrix[i][j] != '*':
                    newNode = self.make_move(i, j)
                    successors.append(newNode)

        # Clear the stored taken positions - saves memory
        self.taken = {}
        return successors


if __name__ == '__main__':
    # global n, p, t_remain, depth_limit, root, optimal

    # To store [optimal score, optimal move, resultant matrix after applying optimal move]
    optimal = []
    # Note down program start time
    start = clock()

    with open('input.txt', 'r') as f:
        n = int(f.readline())
        p = int(f.readline())
        t_remain = float(f.readline())

        # Number of fruits in input
        fruitsFound = 0
        matrix = []
        for i in range(n):
            line = f.readline().strip()
            tmp = []
            for x in line:
                tmp.append(x)
                if x != '*':
                    fruitsFound += 1
            matrix.append(tmp)

    # Init given input as a tree node
    root = node(matrix, 0, fruitsFound)

    # Below if-else ladder is the strategy to choose depth limit of game tree expansion
    # After rigorous research, strategy is made such that the agent can sustain in the game after making maximum
    # number of moves in the worst case

    # Contingency when running out of time
    if (t_remain < 2 and n <= 6) or (t_remain < 5 and n > 6):
        depth_limit = 1

    else:

        if n <= 6:                      # size 1 - 6
            if t_remain > 150:
                depth_limit = 6
            elif t_remain > 30:
                depth_limit = 5
            else:
                depth_limit = 4

        elif n == 7:                     # size 7
            if t_remain > 130:
                depth_limit = 5
            elif t_remain > 40:
                depth_limit = 4
            else:
                depth_limit = 3

        elif n == 8:                     # size 8
            if t_remain > 130 and fruitsFound < (n*n*4)/7:
                depth_limit = 5
            elif t_remain > 45:
                depth_limit = 4
            else:
                depth_limit = 3

        elif n == 9 or n == 10:         # size 9, 10
            if t_remain > 155 and fruitsFound < (n*n*4)/7:
                depth_limit = 5
            elif t_remain > 150:
                depth_limit = 4
            elif t_remain > 65 and fruitsFound < (n*n)/2:
                depth_limit = 4
            else:
                depth_limit = 3

        elif n == 11:                   # size 11
            if t_remain > 240 and fruitsFound < (n*n)/2:
                depth_limit = 5
            elif t_remain > 120:
                depth_limit = 4
            elif t_remain > 55:
                depth_limit = 3
            else:
                depth_limit = 2

        elif n == 12:                   # size 12
            if t_remain > 250 and fruitsFound < (n * n) / 2:
                depth_limit = 5
            elif t_remain > 210:
                depth_limit = 4         # takes around 45 sec
            elif t_remain > 80:
                depth_limit = 3         # takes around 36 sec
            else:
                depth_limit = 2         # takes 0.07 sec

        elif n <= 16:                   # size 13 - 16
            if t_remain > 260:
                depth_limit = 3         # takes around 45 sec

            elif t_remain > 100 and fruitsFound < (n * n) / 4:
                depth_limit = 3
            elif t_remain > 10:
                depth_limit = 2         # takes around 1.4
            else:
                depth_limit = 1         # takes around 0.09

        elif n <= 20:                   # size 17 - 20
            if t_remain > 235 and fruitsFound < (n * n * 4) / 7:
                depth_limit = 3
            elif t_remain > 50:
                depth_limit = 2         # takes around 8 sec
            else:
                depth_limit = 1         # takes around 0.2 sec

        else:                           # size 21 and above
            if (t_remain > 250 and fruitsFound < (n*n)/4) or (t_remain > 140 and fruitsFound < (n*n)/10):
                depth_limit = 3
            elif t_remain > 180:
                depth_limit = 2         # takes around 13
            elif t_remain > 150 and fruitsFound < (n*n)/2:
                depth_limit = 2
            else:
                depth_limit = 1         # takes around 0.6

    # Run mini-max algorithm starting from root node as maximizing entity
    highest_value = MAX_VALUE(root, -maxint, maxint)

    # Write out board obtained after making optimal move and applying gravity
    with open("output.txt", 'w') as f:
        if optimal:
            # The move
            f.write("%s%s\n" % (ascii_uppercase[optimal[1][1]], str(optimal[1][0] + 1)))
            # The resultant board
            for row in optimal[2]:
                f.write(''.join(row)+'\n')

    # print "time taken by shreesh:", clock()-start,'\n\n'
