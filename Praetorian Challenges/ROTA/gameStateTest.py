from gameState import GameState

## Basic Fuzzing Test
## We have the GameState play against itself.
## Since it is a FSM designed to never reach a terminal state, the games should go on indefinitely.
## GameState() will ramdomly select a path given multiple possible moves allowing for complete path coverage eventually.
testPlayer = GameState()

## Run 100 games
for i in range(100):
    state = list('---------')

##    print("%c%c%c" %(state[0],state[1],state[2]))
##    print("%c%c%c" %(state[3],state[4],state[5]))
##    print("%c%c%c\n" %(state[6],state[7],state[8]))
    
    ## Play 100 moves
    for _ in range(100):
        update = testPlayer.get_next_move(state, player=1)

        if len(update) == 1:
            state[update[0] - 1] = 'p'
        else:
            state[update[0] - 1] = '-'
            state[update[1] - 1] = 'p'
            
##        print("Player 1")
##        print("%c%c%c" %(state[0],state[1],state[2]))
##        print("%c%c%c" %(state[3],state[4],state[5]))
##        print("%c%c%c\n" %(state[6],state[7],state[8]))

        update = testPlayer.get_next_move(state, player=-1)
        
        if len(update) == 1:
            state[update[0] - 1] = 'c'
        else:
            state[update[0] - 1] = '-'
            state[update[1] - 1] = 'c'

    print('Game ' + str(i) + ' Done')
            
##        print("Player 2")
##        print("%c%c%c" %(state[0],state[1],state[2]))
##        print("%c%c%c" %(state[3],state[4],state[5]))
##        print("%c%c%c\n" %(state[6],state[7],state[8]))

