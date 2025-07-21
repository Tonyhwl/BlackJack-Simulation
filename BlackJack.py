# started off making lists of all the possible cards and matching them to their corresponding values
# decided to leave the Ace value to later as it is more complex
# I first implemented a very simple while function which allowed me to receive with correct UI
# Added some functions to simplify the while statement later on
# Used a bunch of nested if loops, probably should use for loops for some
# Spent a lot of time debugging, previous experience was GCSE COMSCI so I had to think a lot about where pieces of code belongs for it to work properly
# As of 7/13/25, currently finishing the game and setting up a storage system to look at cards. Main game is finished.
# Still need to add a betting system, storage of past game outcomes. Also need to add a reveal of dealers card at the end of the game.
#stil need to fix the double hit or stand call
#7/21/25 Used the pickle and os libraries to create a file containing a dictionary that allows us to store values even when programs are closed.
#Used for data logging for bets, wins and losses. Next goal: Fix restart, automatic simulations.
#7/21/25 Evening, created an automatic simulation using the martingale betting strategy, simulating 10000+ rounds and plotting
#graphs of log bet size over time and bank balance history
#During 21st to 14th of August, add more statistical analysis and more betting strat selections

import random      #import libraries
import pickle
import os
import matplotlib.pyplot as plt

#set up lists
cr = ['1','2','3','4','5','6','7','8','9','10','Jack','Queen','King','Ace'] #cr = card rank
suits = ['Hearts','Diamonds','Clubs','Spades']
hand = []

#Create empty lists to plot later
bets_history = []
balance_history = []

#set up value mapping for cards
value_mapping = { #cv = card value
    '1' : 1,
    '2' : 2,
    '3' : 3,
    '4' : 4,
    '5' : 5,
    '6' : 6,
    '7' : 7,
    '8' : 8,
    '9' : 9,
    '10' : 10,
    'Jack' : 10,
    'Queen' : 10,
    'King' : 10,
    'Ace' : 11
}

game_state = {
    'player_total' : 0,
    'dealer_total' : 0,
    'player_hand' : [],
    'dealer_hand' : [],
    'wins' : 0,
    'losses' : 0,
    'draws' : 0,
    'balance' : 0,
    'bet' : 100
}

#Creating the pickle file containing wins, losses and bank balance after each game
if os.path.exists("stats.pkl") and os.path.getsize("stats.pkl") > 0:
    with open('stats.pkl', 'rb') as f:
        stats = pickle.load(f)
else:
    stats = {'wins': 0, 'losses': 0, 'draws': 0, 'balance': 1000000}

def random_card():  #creating random cards

    rank = random.choice(cr)
    random_suits = random.choice(suits)
    card = rank + ' of ' + random_suits

    return rank, card


def player_cards(game_state):   #assigning player's cards
    rank, card = random_card()
    game_state['player_hand'].append(card)
    #Ace handling
    if rank == 'Ace':
        # Choose 11 or 1 based on current total
        if game_state['player_total'] + 11 <= 21:
            card_value = 11
        else:
            card_value = 1
    else:
        card_value = value_mapping[rank]
    #Totalling player hand after each randomly assigned card
    game_state['player_total'] += card_value
    #Logging all player cards
    print('Your cards are ', ', '.join(game_state['player_hand']))

#Created a separate function for the start of the game where player gets dealt 2 cards faced up
def initial_player_cards(game_state):
    for i in range (2):
        rank, card = random_card()
        game_state['player_hand'].append(card)
        card_value = value_mapping[rank]
        game_state['player_total'] += card_value

    print('Your cards are ', ', '.join(game_state['player_hand']))

#Assigning dealer's cards
def dealer_cards(game_state):
    while game_state['dealer_total'] < 17:
        rank, card = random_card()
        game_state['dealer_hand'].append(card)
        if rank == 'Ace':
            # Choose 11 or 1 based on current total
            if game_state['dealer_total'] + 11 <= 21:
                d_card_value = 11
            else:
                d_card_value = 1
        else:
            d_card_value = value_mapping[rank]

        game_state['dealer_total'] += d_card_value
        print('Dealer card is ', card)

#Created a separate function for the start of the game where one of the cards for the dealer is facing down
def initial_dealer_cards(game_state): #assigning dealer cards
    rank, card = random_card()
    game_state['dealer_hand'].append(card)
    print('One of the dealers card is ', card)
    dealer_card_value = value_mapping[rank]
    game_state['dealer_total'] += dealer_card_value

    rank,card = random_card()
    game_state['dealer_hand'].append(card)
    dealer_card_value = value_mapping[rank]
    game_state['dealer_total'] += dealer_card_value


def simulate_dealer_cards(game_state):

    while game_state['dealer_total'] < 17:
        rank, card = random_card()
        game_state['dealer_hand'].append(card)
        if rank == 'Ace':
            # Choose 11 or 1 based on current total
            if game_state['dealer_total'] + 11 <= 21:
                d_card_value = 11
            else:
                d_card_value = 1
        else:
            d_card_value = value_mapping[rank]

        game_state['dealer_total'] += d_card_value

def simulate_player_cards(game_state):   #assigning player's cards

    rank, card = random_card()
    game_state['player_hand'].append(card)
    #Ace handling
    if rank == 'Ace':
        # Choose 11 or 1 based on current total
        if game_state['player_total'] + 11 <= 21:
            card_value = 11
        else:
            card_value = 1
    else:
        card_value = value_mapping[rank]
    #Totalling player hand after each randomly assigned card
    game_state['player_total'] += card_value



def show_dealer_hand():
    global run
    print('Dealer\'s hand is ', ', '.join(game_state['dealer_hand']))
    run = False

def checking():
    global run, wins, losses, balance, bet
    if player_total > 21 > dealer_total:
        print('Bust!')
        losses += 1
        balance -= bet
        show_dealer_hand()

    elif dealer_total > 21 > player_total:
        print('You win!')
        wins += 1
        balance += bet
        show_dealer_hand()

    elif player_total == 21 and dealer_total < player_total:
        print('You win!')
        wins += 1
        balance += bet
        show_dealer_hand()

    elif player_total > 21 and dealer_total > 21:
        print('No winners! Play again?')
        show_dealer_hand()

    elif dealer_total == 21 and player_total < dealer_total:
        print ('Dealer wins!')
        losses += 1
        balance -= bet
        show_dealer_hand()


def game_run():
    global run, losses, wins, balance, bet
    if not run:
        return

    while run:
        if 21 >= player_total >= 0 and 21>=dealer_total>=0:
            prompt = input('Hit or stand?')

            if prompt == 'stand':
                if dealer_total < 17:
                    dealer_cards(game_state)
                checking()
                if not run:
                    return
                elif 17 <= dealer_total < 21:
                    player_difference = 21 - player_total
                    dealer_difference = 21 - dealer_total
                    if player_difference < dealer_difference:
                        print('You win!')
                        wins += 1
                        balance += bet
                        show_dealer_hand()
                    elif player_difference > dealer_difference:
                        print('You lose!')
                        losses += 1
                        balance -= bet
                        show_dealer_hand()
                    elif player_difference == dealer_difference:
                        print('Draw!')
                        show_dealer_hand()
                    run = False
                return

            elif prompt == 'hit':
                player_cards(game_state)
                checking()
                if not run:
                    return


def martingale_strategy(game_state):
    # Reset for new round
    game_state['player_total'] = 0
    game_state['dealer_total'] = 0
    game_state['player_hand'] = []
    game_state['dealer_hand'] = []

    # Player hits until total > 17
    while game_state['player_total'] <= 17:
        simulate_player_cards(game_state)

    # Dealer hits until total >= 17
    while game_state['dealer_total'] < 17:
        simulate_dealer_cards(game_state)

    martingale_checking(game_state)

def martingale_checking(game_state):
    pt = game_state['player_total']
    dt = game_state['dealer_total']
    bet = game_state['bet']

    # Player busts
    if pt > 21 and dt <= 21:
        game_state['losses'] += 1
        game_state['balance'] -= bet
        game_state['bet'] *= 2

    # Dealer busts
    elif dt > 21 and pt <= 21:
        game_state['wins'] += 1
        game_state['balance'] += bet
        game_state['bet'] = 100

    # Both bust = draw
    elif pt > 21 and dt > 21:
        game_state['draws'] += 1

    # Player blackjack
    elif pt == 21 and dt < 21:
        game_state['wins'] += 1
        game_state['balance'] += bet
        game_state['bet'] = 100

    # Dealer blackjack
    elif dt == 21 and pt < 21:
        game_state['losses'] += 1
        game_state['balance'] -= bet
        game_state['bet'] *= 2

    # Normal comparison
    else:
        if pt > dt:
            game_state['wins'] += 1
            game_state['balance'] += bet
            game_state['bet'] = 100
        elif pt < dt:
            game_state['losses'] += 1
            game_state['balance'] -= bet
            game_state['bet'] *= 2
        else:
            game_state['draws'] += 1



#reset counters after every simulation
game_state['wins'] = 0
game_state['losses'] = 0
game_state['draws'] = 0
game_state['balance'] = 1000000

#run manual or automatic simulation of Blackjack
print("Your bank balance is: ", game_state['balance'])
version = input('Automatic or Manual? (a/m)')
if version == 'a':
    initial_player_cards(game_state)
    initial_dealer_cards(game_state)
    game_state['bet'] = 100
    for i in range(10000):
        martingale_strategy(game_state)
        game_state['player_total'] = 0
        game_state['dealer_total'] = 0

        # Add on each value of bets, balance after each round
        bets_history.append(game_state['bet'])
        balance_history.append(game_state['balance'])

        # Save wins, losses, draws, balance to pickle file
        with open('stats.pkl', 'wb') as f:  # wb = write binary (for saving)
            pickle.dump({'wins': game_state['wins'], 'losses': game_state['losses'], 'draws': game_state['draws'], 'balance': game_state['balance']}, f)

        # print out stats after each successful game
        print(f"Wins: {game_state['wins']}, Losses: {game_state['losses']}, Draws: {game_state['draws']}, Balance: {game_state['balance']}")
        # End game when money runs out
        if game_state['balance'] < 0:
            print('Not enough money!')
            break


elif version == 'm':

    # Dealing initial cards
    if balance <= 0:
        balance += 1000

    initial_player_cards()
    initial_dealer_cards()
    bet_bool = False
    while not bet_bool:
        bet_input = int(input('How much would you like to bet? '))
        bet = bet_input
        if 0 < bet <= balance:
            bet_bool = True
            break
        else:
            print('Invalid amount of bet!')

    # Running the game
    while run:

        game_run()

        # saving data to the pickle file in order for it to be stored even when program closes

        with open('stats.pkl', 'wb') as f:  # wb = write binary (for saving)
            pickle.dump({'wins': wins, 'losses': losses,'draws':draws, 'balance': balance}, f)

        # print out stats after each successful game
        print(f'wins: {wins}, losses: {losses}, draws: {draws}, balance: {balance}')

        # End game when money runs out
        if balance < 0:
            print('Not enough money!')
            break





print(len(balance_history), len(bets_history))
size = str(len(bets_history))

#Plotting graphs of bet history against game number and bank balance against game number
plt.semilogy(bets_history)
plt.title("Bet Size Over Time (Martingale) after " + size + ' games')
plt.xlabel("Game Number")
plt.ylabel("Bet Size (Log base 10)")
plt.grid(True)
plt.show()

plt.plot(balance_history)
plt.title("Balance Over Time (Martingale) after " + size + ' games')
plt.xlabel("Game Number")
plt.ylabel("Balance")
plt.grid(True)
plt.show()

#Conclusion:





























