# Praetorian Challenge: ROTA

### Requirements
* Python Version: 3.6.8

This code is for the [Praetorian ROTA Challenge](https://www.praetorian.com/challenges/rota).

### File Summaries
* __ROTA.py__ is the main script that will complete the challenge.
* __boardState.py__ contains the BoardState class, which is a node of an FSM. A BoardState object stores a possible board state, whether the state leads to a victory or loss, and possible moves to other BoardState objects.
* __gameState.py__ contains the logic to generate the FSM of all board states and the logic to remove all moves that would terminate the game.
* __gameStateTest.py__ contains code used to test and debug __gameState.py__.

### How To Use
1. Change the email set in __ROTA.py__.
2. Run __ROTA.py__.

### Algorithms
To generate the FSM that cannot lose:
1. Generate a FSM of all board states.
1. Populate all edges by simulating every possible move in a state.
1. Find all winning states (a player has three-in-a-row) and mark the state as terminal and remove all edges from the state.
1. Add all terminal states to a queue.
1. Iterate through all states in the queue and remove all edges to the state.
1. For every state that had an edge removed, check if the state has no edges remaining.
1. If a state has no possible moves remaining, mark it as a terminal state and add it to the queue.
1. Repeat steps 4-7 until the queue is empty.

The actual implementation is a bit more complicated because I do not create a boardState object for each board state. To improve the performance of generating the FSM, 
I have a single boardState object represent all rotations, reversed rotations, and player-swapped representations.

For Example:  
<pre>
 1  0 -1                     -1  0  0                      1  0  0                      0  0  1

-1  1  0   is equivalent to   0  1  1   is equivalent to   0 -1 -1   is equivalent to  -1 -1  0

-1  1  0                      1 -1 -1                     -1  1  1                      1  1 -1
</pre>
This requires an additional layer of translation to translate states to objects and move positions, but it greatly decrease the number of nodes I need to iterate through and the number of edges I need to prune.