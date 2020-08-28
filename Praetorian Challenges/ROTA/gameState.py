from random import sample
from boardState import BoardState

## GameState.boardStates[center][state] = (BoardState, rotation, isReversed, isPlayerSwitched)
## GameState.allStates: A set of all BoardState objects

class GameState:
    def __init__(self):
        self.boardStates = [dict(), dict(), dict()]
        self.allStates = set()

        self._generate_board_states()
        self._connect_states()
        self._prune_connections()

    ## Generates all possible board states as keys that map to the corresponding boardState object
    def _generate_board_states(self):
        ## List of all possible piece counts [Player 2, Empty, Player 1]
        moveNum = [[0, 9, 0], [0, 8, 1], [1, 7, 1], [1, 6, 2], [2, 5, 2], [2, 4, 3], [3, 3, 3]]
        center = 0
        permutation = [0] * 8

        for avalible in moveNum:
            for index in range(3):
                if avalible[index] > 0:
                    center = index - 1
                    avalible[index] -= 1
                    self._generate_permutations(permutation, center, avalible, 0)
                    avalible[index] += 1

    ## Generates all permutations given set of number of 0's, 1's, and -1's
    def _generate_permutations(self, permutation, center, available, index):
        if index == 7:
            if available[0]:
                permutation[index] = -1
            elif available[1]:
                permutation[index] = 0
            else:
                permutation[index] = 1

            state = tuple(permutation)
            
            if state in self.boardStates[center]:
                pass
            else:
                bState = BoardState(center, state)

                ## Make sure not impossible state (both players have three-in-a-row)
                if not (bState.winner[(1,-1)] and bState.winner[(-1, 1)]):
                    self._generate_shift_reverse(bState)
                    self.allStates.add(bState)
        else:
            ## Recursion
            for i in range(3):
                if available[i] > 0:
                    permutation[index] = i - 1
                    available[i] -= 1
                    self._generate_permutations(permutation, center, available, index + 1)
                    available[i] += 1

    ## Given a boardState object, generate all rotations, reverse rotations and player swapped states.
    ## Map these keys to a tuple of (BoardState object, rotation_shift, isReversed, isPlayerSwitched)
    def _generate_shift_reverse(self, bState):
        state = list(bState.state) + list(bState.state)
        center = bState.center

        ## Normal Rotations
        for i in range(8):
            key = tuple(state[i:i+8])
            if key in self.boardStates[center]:
                pass
            else:
                self.boardStates[center][key] = (bState, i, False, 1)

        state.reverse()
        
        ## Reversed Rotations
        for i in range(8):
            key = tuple(state[i:i+8])
            if key in self.boardStates[center]:
                pass
            else:
                self.boardStates[center][key] = (bState, i, True, 1)

        state, center = GameState._switch_players(state, center)

        ## Reversed Player-Swapped Rotations
        for i in range(8):
            key = tuple(state[i:i+8])
            if key in self.boardStates[center]:
                pass
            else:
                self.boardStates[center][key] = (bState, i, True, -1)

        state.reverse()

        ## Normal Player-Swapped Rotations
        for i in range(8):
            key = tuple(state[i:i+8])
            if key in self.boardStates[center]:
                pass
            else:
                self.boardStates[center][key] = (bState, i, False, -1)

    ## Switches player pieces (1 -> -1) and (-1 -> 1)        
    def _switch_players(state, center):
        for index in range(16):
            state[index] *= -1

        return state, -center

    ## Generate all possible moves from a BoardState and store move information in BoardState.nextStates
    ## Move: ((from, to), boardState object, isPlayerSwitched)
    ## Place: ((place, ), boardState object, isPlayerSwitched)
    ## Center is denoted as -1, rest are as indices of BoardStat.state
    def _connect_states(self):
        for bState in self.allStates:
            p1Count = bState.pieceCount[1]
            p2Count = bState.pieceCount[-1]
            
            ## If p1Count == p2Count == 3, either player moves
            ## If p1Count == p2Count < 3, either player adds a piece
            ## If p1Count > p2Count, p2 adds a piece
            ## If p2Count > p1Count, impossible because of how the states were generated

            if bState.gameOver == False:
                if p2Count < p1Count:
                    self._connect_states_add(bState, -1)
                elif p1Count < 3:
                    self._connect_states_add(bState, 1)
                    self._connect_states_add(bState, -1)
                else:
                    self._connect_states_move(bState, 1)
                    self._connect_states_move(bState, -1)

    ## Generate all possible placement moves for a given player and BoardState
    def _connect_states_add(self, bState, player):
        state = list(bState.state)
        center = bState.center

        ## Center
        if center == 0:
            nextState, _, _, switchPlayer = self.boardStates[player][tuple(state)]
            bState.nextStates[player].add(((-1,), nextState, switchPlayer))

        ## Ring
        for index in range(8):
            if state[index] == 0:
                state[index] = player
                nextState, _, _, switchPlayer = self.boardStates[center][tuple(state)]
                bState.nextStates[player].add(((index,), nextState, switchPlayer))
                state[index] = 0

    ## Generate all possible moves for a given player and BoardState
    def _connect_states_move(self, bState, player):
        state = list(bState.state)
        center = bState.center

        ## Center Piece
        if center == player:
            for index in range(8):
                if state[index] == 0:
                    state[index] = player
                    nextState, _, _, switchPlayer = self.boardStates[0][tuple(state)]
                    bState.nextStates[player].add(((-1, index), nextState, switchPlayer))
                    state[index] = 0

        ## Ring Piece
        for index in range(8):
            if state[index] == player:
                if center == 0:
                    state[index] = 0
                    nextState, _, _, switchPlayer = self.boardStates[player][tuple(state)]
                    bState.nextStates[player].add(((index, -1), nextState, switchPlayer))
                    state[index] = player

                if state[(index - 1)] == 0:
                    state[(index - 1)] = player
                    state[index] = 0
                    nextState, _, _, switchPlayer = self.boardStates[center][tuple(state)]
                    bState.nextStates[player].add(((index, (index - 1) % 8), nextState, switchPlayer))
                    state[(index - 1)] = 0
                    state[index] = player

                if state[(index + 1) % 8] == 0:
                    state[(index + 1) % 8] = player
                    state[index] = 0
                    nextState, _, _, switchPlayer = self.boardStates[center][tuple(state)]
                    bState.nextStates[player].add(((index, (index + 1) % 8), nextState, switchPlayer))
                    state[(index + 1) % 8] = 0
                    state[index] = player

    def _prune_connections(self):
        queue = set()
        nextQueue = set()

        ## Find all game ending states (a player has three-in-a-row)
        for bState in self.allStates:
            if bState.gameOver:
                if bState.pieceCount[-1] == bState.pieceCount[1]:
                    queue.add(bState)

        self._prune_helper(queue, nextQueue, self._undo_move)

        queue = set()
        nextQueue = set()

        ## Find all losing states and winning states
        for bState in self.allStates:
            if bState.winner[(1,-1)] or bState.winner[(-1,1)]:
                queue.add(bState)
            if bState.winner[(1,1)] or bState.winner[(-1,-1)]:
                nextQueue.add(bState)

        self._prune_helper(queue, nextQueue, self._undo_place)

    ## Find all winning moves and remove all losing moves
    def _prune_helper(self, queue, nextQueue, undoFunction):
        while len(queue) != 0:
            ## Loop through opponent's (-player) losing states to find my (player) winning states.
            for bState in queue:
                for player in (1, -1):
                    if bState.winner[(player, -player)] == True:
                        if bState.center == player:
                            undoFunction(bState, -1, GameState._winning_move, nextQueue)

                        for index, value in enumerate(bState.state):
                            if value == player:
                                undoFunction(bState, index, GameState._winning_move, nextQueue)

            queue = nextQueue
            nextQueue = set()

            ## Loop through opponent's (-player) winning states and remove from my (player) nextStates.
            for bState in queue:
                for player in (1,-1):
                    if bState.winner[(-player, -player)] == True:
                        if bState.center == player:
                            undoFunction(bState, -1, GameState._losing_move, nextQueue)

                        for index, value in enumerate(bState.state):
                            if value == player:
                                undoFunction(bState, index, GameState._losing_move, nextQueue)

            queue = nextQueue
            nextQueue = set()

    ## Given a BoardState undo a move and remove the move from prevState
    def _undo_move(self, bState, index, removalFunction, nextQueue):
        center =  bState.center
        state = list(bState.state)

        ## Center piece
        if index == -1:
            for i, value in enumerate(bState.state):
                if value == 0:
                    state[i] = center
                    
                    prevState, _, _, switch = self.boardStates[0][tuple(state)]
                    
                    if removalFunction(bState, prevState, center*switch) == True:
                        nextQueue.add(prevState)
                        
                    state[i] = 0
                    
        ## Ring Piece
        else:
            player = state[index]
            
            if center == 0:
                center = player
                state[index] = 0
                
                prevState, _, _, switch = self.boardStates[center][tuple(state)]
                
                if removalFunction(bState, prevState, player*switch) == True:
                    nextQueue.add(prevState)
        
                center = 0
                state[index] = player
                
            if state[(index - 1)] == 0:
                state[(index - 1)] = player
                state[index] = 0
                
                prevState, _, _, switch = self.boardStates[center][tuple(state)]
                
                if removalFunction(bState, prevState, player*switch) == True:
                    nextQueue.add(prevState)
        
                state[(index - 1)] = 0
                state[index] = player
            
            if state[(index + 1) % 8] == 0:
                state[(index + 1) % 8] = player
                state[index] = 0
                prevState, _, _, switch = self.boardStates[center][tuple(state)]

                if removalFunction(bState, prevState, player*switch) == True:
                    nextQueue.add(prevState)
        
                state[(index + 1) % 8] = 0
                state[index] = player

    ## Given a BoardState undo a place and remove the move from prevState
    def _undo_place(self, bState, index, removalFunction, nextQueue):
        center = bState.center
        state = list(bState.state)

        ## Center Piece
        if index == -1:
            prevState, _, _, switch = self.boardStates[0][tuple(state)]
                    
            if removalFunction(bState, prevState, center*switch) == True:
                nextQueue.add(prevState)
        ## Ring Piece
        else:
            player = state[index]
            state[index] = 0
            prevState, _, _, switch = self.boardStates[center][tuple(state)]
            
            if removalFunction(bState, prevState, player*switch) == True:
                nextQueue.add(prevState)

    ## Remove all moves for player from prevState except to bState.
    ## Set prevState.winner[(player, player)] to True
    ## If prevState did not already have a winning move, return True so that prevState is added to nextQueue
    def _winning_move(bState, prevState, player):
        temp = []
        
        if prevState.winner[(player, player)] == False and prevState.gameOver == False:
            for nextStateInfo in prevState.nextStates[player]:
                if nextStateInfo[1] == bState:
                    temp.append(nextStateInfo)

            prevState.nextStates[player] = set(temp)
            prevState.winner[(player, player)] = True
            return True

        return False

    ## Remove moves for player from prevState to bState.
    ## If player has no moves remaining, set prevState.winner[(-player, player)] to True
    ## If prevState did not already guarantee a loss, return True so that prevState is added to nextQueue
    def _losing_move(bState, prevState, player):
        temp = []
        
        if prevState.winner[(-player, player)] == False and prevState.gameOver == False:
            for nextStateInfo in prevState.nextStates[player]:
                if nextStateInfo[1] == bState:
                    temp.append(nextStateInfo)

            prevState.nextStates[player].difference_update(temp)

            ## Special state that is the same reversed and player-swapped
            ## Player 1 and Player -1 will make the same moves (with difference indices)
            ## Since we cannot differentiate which player is actually moving, we manually check for this state and repeat the process for both players.
            if prevState.state == (-1, 0, 1, -1, 0, 1, -1, 1) and prevState.center == 0:
                for nextStateInfo in prevState.nextStates[-player]:
                    if nextStateInfo[1] == bState:
                        temp.append(nextStateInfo)

                prevState.nextStates[-player].difference_update(temp)

            ## If player has no moves left, prevState is a losing state
            if len(prevState.nextStates[player]) == 0:
                prevState.winner[(-player, player)] = True
                return True

        return False
        
    ## Translation function to translate from server state representation to a BoardState object
    ## Gets next move from BoardState object
    ## Translates piece positions back to server representation
    def get_next_move(self, charState, player=1):
        temp = [charState[0], charState[1], charState[2], charState[5], charState[8], charState[7], charState[6], charState[3]]
        translate = [1,2,3,6,9,8,7,4,5]
        state = [0] * 8
        center = 0

        ## Translate  'p' and 'c' to 1 and -1
        if charState[4] == 'p':
            center = 1
        elif charState[4] == 'c':
            center = -1

        for index, char in enumerate(temp):
            if char == 'p':
                state[index] = 1
            elif char == 'c':
                state[index] = -1

        ## Lookup BoardState
        bState, shift, isReversed, switchPlayer = self.boardStates[center][tuple(state)]

        ## Just pick a random move (all remaining moves are non-losing moves)
        nextMove = sample(bState.nextStates[player*switchPlayer], 1)[0][0]

        ## Move is a place
        if len(nextMove) == 1:
            moveFrom = nextMove[0]
            
            if moveFrom != -1:
                if isReversed:
                    moveFrom = 7 - moveFrom

                moveFrom = (moveFrom - shift) % 8

            if moveFrom == -1:
                assert center == 0
            else:
                assert state[moveFrom] == 0
                
            return (translate[moveFrom], )

        ## Move is normal move
        else:
            moveFrom = nextMove[0]
            moveTo = nextMove[1]

            if moveFrom != -1:
                if isReversed:
                    moveFrom = 7 - moveFrom

                moveFrom = (moveFrom - shift) % 8

            if moveTo != -1:
                if isReversed:
                    moveTo = 7 - moveTo
                    
                moveTo = (moveTo - shift) % 8

            if moveFrom == -1:
                assert center == player
            else:
                assert state[moveFrom] == player
            
            if moveTo == -1:
                assert center == 0
            else:
                assert state[moveTo] == 0

        return (translate[moveFrom], translate[moveTo])
