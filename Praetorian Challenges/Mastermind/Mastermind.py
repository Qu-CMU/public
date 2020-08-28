import requests
import json
import sys
from Gladiator import Gladiator

if sys.version_info < (3,0):
    sys.exit('Python version < 3.0 does not support modern TLS versions. You will have trouble connecting to our API using Python 2.X.')

## Constants
email = 'johnsmith@email.com' ## Change Me
url = 'https://mastermind.praetorian.com'

headers = dict()
headers['Content-Type'] = 'application/json'
r = requests.post('{0}/api-auth-token/'.format(url), data={'email':email})
auth_token = r.json()['Auth-Token']
headers['Auth-Token'] = auth_token

## Globals
level_num = 1

## ----------------------------------------------------------------------------------------------
## Communitation Code

## Resets game back to level 1
def reset_levels():
    response = requests.post('{0}/reset/'.format(url), headers=headers)
    r = response.json()
    
    if 'error' in r:
        print('Error Message: ' + r['error'])
    else:
        print("Successfully Reset Levels")

## Save hash to '{email}_hash.txt' if avalible
def get_hash():
    response = requests.get('{0}/hash/'.format(url), headers=headers)
    r = response.json()
    
    if 'error' in r:
        print('Error Message: ' + r.json()['error'])
    elif 'hash' in r:
        print("Saving hash to " + email + "_hash.txt")
        f = open(email + "_hash.txt","w")
        f.write("Email: {0}\nAuth-Token: {1}\nHash: {2}".format(email, auth_token, r['hash']))
        sys.exit()

## Start level 'num'
## Return level parameters
def start_level(num):
    response = requests.get('{0}/level/{1}/'.format(url, num), headers=headers)
    r = response.json()

    if 'error' in r:
        print('Error Message: ' + r['error'])
        sys.exit()

    print("Starting Level " + str(level_num))
    print('Num Weapons: {0}\nNum Gladiators: {1}\nMax Guesses: {2}\nNum Rounds: {3}\n'.format(r['numWeapons'], r['numGladiators'], r['numGuesses'] ,r['numRounds']))
    return r

## Send a guess
## Return response
def send_guess(guess):
    response = requests.post('{0}/level/{1}/'.format(url, level_num), data=json.dumps({'guess':list(guess)}), headers=headers)
    r = response.json()
    
    if 'error' in r:
        print('Error Message: ' + r['error'])
        sys.exit()
    else:
        print("Sent Guess: " + str(guess))
        return r

## ----------------------------------------------------------------------------------------------
## Play the game
    
if __name__ == '__main__':
    reset_levels()

    while(True):
        r = start_level(level_num)
        Hercules = Gladiator(r['numWeapons'], r['numGladiators'])
        
        for i in range(r['numRounds']):
            print('Round: ' + str(i+1))
            for _ in range(r['numGuesses']):
                r = send_guess(Hercules.get_next_guess())
                if 'roundsLeft' in r:
                    Hercules.reset()
                    break
                elif 'hash' in r:
                    get_hash()
                elif 'message' in r:
                    break
                else:
                    Hercules.update(r['response'][0], r['response'][1])

        print("Level " + str(level_num) + " finished\n")
        level_num += 1
