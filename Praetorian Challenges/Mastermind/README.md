# Praetorian Challenge: Mastermind

### Requirements
* Python Version: 3.6.8

This code is for the [Praetorian Mastermind Challenge](https://www.praetorian.com/challenges/mastermind).

### File Summaries
* __Mastermind.py__ is the main script that will complete the challenge.
* __Gladiator.py__ contains most of the logic used to determine the best next guess and which codes are still possible.
* __weaponDeduction.py__ contains specialized logic for reducing the combination search space when it is too large to be enumerated.
* __Util.py__ contain various functions that are used in multiple files.
* __*Test.py__ contains code used to test and debug each of their respective classes.

### How To Use
1. Change the email set in __Mastermind.py__.
1. Run __Mastermind.py__.

### Algorithms
The primary guessing algorithm used in the logic is a variation of [Kunth's Mastermind Algorithm](https://en.wikipedia.org/wiki/Mastermind_(board_game)#Worst_case:_Five-guess_algorithm) (KMA). 
Gladiator.py contains various different approximations of KMA depending on the size of the search space in order to make a reasoned guess within the time limit.

These approximations include:
* Only considering possible permutations as guesses, even though an impossible permutation can be a more optimal guess. 
* Randomly selecting a subset of all possible permutations and running KMA over the subset to approximate the larger set.
* Implement a best-effort approach of finding the best guess out of every guess the program had time to check, rather than out of every guess.
* If the number of permutations is too large, we apply these concepts to code combinations in an effort to reduce the number of possible combinations.

Deduction primarily involves removing permutations/combinations from lists/sets if a guess is checked against the permutation/combination and the simulated response does not match the response given by the server. 
__WeaponDeduction.py__ uses an entirely different algorithm based on set differences to reduce the combination search space until it can be enumerated.