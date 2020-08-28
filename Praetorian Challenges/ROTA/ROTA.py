import requests
import json
import sys
from gameState import GameState
import time

email = 'johnsmith@email.com'
baseURL = 'http://rota.praetorian.com/rota/service/play.php?request='
cookie = None

## ----------------------------------------------------------------------
## Communication code

def new_game():
    global cookie
    url = '{url}new&email={email}'
    requestURL = url.format(url=baseURL, email=email)
    r = requests.get(requestURL)
    response = r.json()
    cookie = r.cookies

    if response['status'] == 'success':
        return response['data']['board']

    print("Error: \'new_game\'\n" + str(response))
    sys.exit()

def place(x):
    global cookie
    url = '{url}place&location={location}'
    requestURL = url.format(url=baseURL, location=x)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        return response['data']['board']

    print("Error: \'place\'\n" + str(response))
    sys.exit()

def move(x, y):
    global cookie
    url = '{url}move&from={oldLocation}&to={newLocation}'
    requestURL = url.format(url=baseURL, oldLocation=x, newLocation=y)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        return response['data']['moves'], response['data']['board']

    print("Error \'move\':\n" + str(response))
    sys.exit()

def status():
    global cookie
    url = '{url}status&email={email}'
    requestURL = url.format(url=baseURL, email=email)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        return response['data']

    print("Error \'status\'\n" + str(response))
    sys.exit()

def next_game():
    global cookie
    url = '{url}next'
    requestURL = url.format(url=baseURL)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        if 'hash' in response['data']:
            get_hash(response['data']['hash'])
        else:
            return response['data']['games_won'], response['data']['board']

    print("Error \'next\'\n" + str(response))
    sys.exit()

def get_hash(hashString):
    print("Saving hash to " + email + "_hash.txt")
    f = open(email + "_hash.txt","w")
    f.write("Email: " + email +  "\nHash: " + hashString)
    sys.exit()

##------------------------------------------------------------------------------------------
## Play the game
    
if __name__ == '__main__':
    player = GameState()
    state = new_game()
    numMoves = 0
    numGames = 0
    startTime = time.time()

    ## Play games until hash recieved (challenge requires 50 games)
    while True:
        print('Game Number: {0}'.format(numGames))
        print('Time Elapsed: {0:3f}'.format(time.time() - startTime))

        ## Make moves until game is over (games requires you make 30 moves without losing.)
        while numMoves < 30:
    ##        print(str(state[0]) + str(state[1]) + str(state[2]))
    ##        print(str(state[3]) + str(state[4]) + str(state[5]))
    ##        print(str(state[6]) + str(state[7]) + str(state[8]))
    ##        print('\n')
            
            moveInfo = player.get_next_move(state)

            if len(moveInfo) == 1:
                state = place(moveInfo[0])
            else:
                numMoves, state = move(moveInfo[0], moveInfo[1])
        
        numGames, state = next_game()
        numMoves = 0
