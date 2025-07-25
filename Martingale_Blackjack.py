import random      #import libraries
import pickle
import os
import matplotlib.pyplot as plt
import numpy as np

#set up lists
cr = ['1','2','3','4','5','6','7','8','9','10','Jack','Queen','King','Ace'] #cr = card rank
suits = ['Hearts','Diamonds','Clubs','Spades']

#create empty lists to plot later
bet_history = []
balance_history = []

session_bet_history = []
session_balance_history = []
session_returns = []

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
    'bet' : 0,
    'original_balance' : 10000,
    'original_bet' : 500,
    'session_returns': 0,
    'ruin_counter':0
}

total_wins = 0
total_losses = 0
total_draws = 0
total_ruin_counter = 0
num_simulations = 1000

#Creating the pickle file containing wins, losses and bank balance after each game
if os.path.exists("m_stats.pkl") and os.path.getsize("m_stats.pkl") > 0:
    with open('m_stats.pkl', 'rb') as f:
        stats = pickle.load(f)

def random_card():  #creating random cards

    rank = random.choice(cr)
    random_suits = random.choice(suits)
    card = rank + ' of ' + random_suits

    return rank, card

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

def m_win(game_state):
    game_state['wins'] += 1
    game_state['balance'] += game_state['bet']
    game_state['bet'] = game_state['original_bet']

def m_loss(game_state):
    game_state['losses'] += 1
    game_state['balance'] -= game_state['bet']
    game_state['bet'] *= 2

def m_draw(game_state):
    game_state['draws'] += 1
    game_state['bet'] = game_state['original_bet']

def martingale_strategy(game_state):
    # Reset for new round
    game_state['player_total'] = 0
    game_state['dealer_total'] = 0
    game_state['player_hand'] = []
    game_state['dealer_hand'] = []

    # Player hits until total > 17
    while game_state['player_total'] < 17:
        simulate_player_cards(game_state)

    # Dealer hits until total >= 17
    while game_state['dealer_total'] < 17:
        simulate_dealer_cards(game_state)

    martingale_checking(game_state)

def martingale_checking(game_state):
    pt = game_state['player_total']
    dt = game_state['dealer_total']

    # Player busts
    if pt > 21 and dt <= 21:
        m_loss(game_state)

    # Dealer busts
    elif dt > 21 and pt <= 21:
        m_win(game_state)

    # Both bust = draw
    elif pt > 21 and dt > 21:
        m_draw(game_state)

    # Player blackjack
    elif pt == 21 and dt < 21:
        m_win(game_state)

    # Dealer blackjack
    elif dt == 21 and pt < 21:
        m_loss(game_state)

    # Normal comparison
    else:
        if pt > dt:
            m_win(game_state)
        elif pt < dt:
            m_loss(game_state)
        else:
            m_draw(game_state)

#reset counters after every simulation
def reset(game_state):
    game_state['wins'] = 0
    game_state['losses'] = 0
    game_state['draws'] = 0

    game_state['balance'] = game_state['original_balance']
    game_state['bet'] = game_state['original_bet']

def pickle_save(game_state):
    # Save wins, losses, draws, balance to pickle file
    with open('m_stats.pkl', 'wb') as f:  # wb = write binary (for saving)
        pickle.dump({'wins': game_state['wins'], 'losses': game_state['losses'], 'draws': game_state['draws'],
                     'balance': game_state['balance']}, f)

    # print out stats after each successful game
    print(
        f"Wins: {game_state['wins']}, Losses: {game_state['losses']}, Draws: {game_state['draws']}, Balance: {game_state['balance']}")


#run automatic simulation of Blackjack
def martingale_run(game_state):
    global num_simulations, total_wins, total_losses, total_draws, total_ruin_counter

    reset(game_state)
    for i in range(num_simulations):
        game_state['balance'] = game_state['original_balance']
        game_state['bet'] = game_state['original_bet']
        game_state['wins'] = 0
        game_state['losses'] = 0
        game_state['draws'] = 0
        game_state['ruin_counter'] = 0
        for j in range(100):
         martingale_strategy(game_state)
         game_state['player_total'] = 0
         game_state['dealer_total'] = 0

         # Add on each value of bets, balance after each round
         bet_history.append(game_state['bet'])
         balance_history.append(game_state['balance'])

         pickle_save(game_state)
        # End game when money runs out
         if game_state['balance'] <= 0:
             game_state['balance'] = 0
             game_state['ruin_counter'] += 1
             print('Not enough money!')
             break
         elif game_state['bet'] > game_state['balance']:
             game_state['ruin_counter'] += 1
             break

        total_wins += game_state['wins']
        total_losses += game_state['losses']
        total_draws += game_state['draws']
        total_ruin_counter += game_state['ruin_counter']

        session_balance_history.append(balance_history[-1])
        game_state['session_returns'] = (session_balance_history[-1] - game_state['original_balance'])
        session_returns.append(game_state['session_returns'])
        session_bet_history.append(np.mean(bet_history))
        print('One session finished.')

martingale_run(game_state)

#statistical analysis section
size = str(len(session_balance_history))

#Plotting graphs of bet history against game number and bank balance against game number
plt.plot(session_bet_history)
plt.title("Mean Bet Size Over Time (Martingale) after " + size + ' sessions')
plt.xlabel("Session Number")
plt.ylabel("Bet Size (£)")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.plot(session_balance_history)
plt.title("Balance Over Time (Martingale) after " + size + ' sessions')
plt.xlabel("Session Number")
plt.ylabel("Balance (£)")
plt.grid(True)
plt.tight_layout()
plt.show()

def calculate_max_drawdown(balance_history):
    balance_history = np.array(balance_history)
    running_max = np.maximum.accumulate(balance_history)
    drawdowns = (running_max - balance_history) / running_max
    return np.max(drawdowns)

total_played_hands = total_wins + total_losses + total_draws
win_rate = total_wins / total_played_hands
loss_rate = total_losses / total_played_hands
average_bet = sum(bet_history) / len(bet_history)
mean_return = np.mean(game_state['session_returns'])
standard_deviation_returns = np.std(session_returns, ddof = 1) #calculating sample standard deviation so we use ddof = 1
sharpe_ratio = mean_return / standard_deviation_returns
ruin_probability = total_ruin_counter / 1000
drawdown = calculate_max_drawdown(balance_history)

print('Total simulations (of 100 games): ', 1000)
print(f'Total complete games played: ',total_played_hands)
print(f'Win rate: ', win_rate*100, '%')
print(f'Loss rate: ', loss_rate*100, '%')
print(f'Average bet: ', average_bet)
print(f'Expected value per run: ', mean_return)
print(f'Standard deviation of returns: ', standard_deviation_returns)
print(f'Sharpe ratio: ', sharpe_ratio)
print(f'Ruin probability: ', ruin_probability*100, '%')
print(f'Max drawdown: ', drawdown*100, '%')






























