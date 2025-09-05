#import libraries
import pickle
import matplotlib.pyplot as plt
import numpy as np,math

#set up lists
cr = ['2','3','4','5','6','7','8','9','10','Jack','Queen','King','Ace'] #cr = card rank
suits = ['Hearts','Diamonds','Clubs','Spades']

#Create empty lists to plot later
bet_history = []
balance_history = []
loss_per_100u_list = []
ev_per_hand_list = []
session_bet_history = []
session_balance_history = []
session_returns = []
session_pct_returns = []
max_drawdowns = []

#set up value mapping for cards
value_mapping = {
#cv = card value
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
    'original_bet' : 200,
    'session_returns': 0,
    'ruin_counter':0
}

total_wins = 0
total_losses = 0
total_draws = 0
total_ruin_counter = 0
num_simulations = 10000
hands_per_session = 500
TABLE_MIN = 100          # 1u
TABLE_MAX = 4000        # 40u
BANKROLL_CAP = 10000     # 100u
frac = 0.02
rng = np.random.default_rng(seed=42) # faster, reproducible randomness

#Creating the pickle file containing wins, losses and bank balance after each game
#if os.path.exists("f_stats.pkl") and os.path.getsize("f_stats.pkl") > 0:
    #with open('f_stats.pkl', 'rb') as f:
        #stats = pickle.load(f)

def random_card():
    rank_idx = rng.integers(0, len(cr))   # random index for ranks etc. 10 = Queen
    suit_idx = rng.integers(0, len(suits))  # random index for suits etc. 3 = Clubs

    rank = cr[rank_idx] # Match index with card
    suit = suits[suit_idx] # Match index with suit

    return rank, f"{rank} of {suit}"

def current_total_and_soft(hand):
    total, aces = 0, 0 # aces = number of aces seen

    #loop through every card in the player's or dealer's hand
    for card in hand:
        rank = card.split(' of ')[0] # only want the rank part of 'Queen of Spades' etc.
        v = 11 if rank == 'Ace' else value_mapping[rank]
        total += v
        if rank == 'Ace':
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1

    # If any Ace is still counted as 11 → hand is "soft", else it's "hard"
    return total, (aces > 0)

def simulate_dealer_cards(game_state):
    while True:
        dt, _ = current_total_and_soft(game_state['dealer_hand'])
        game_state['dealer_total'] = dt

        if dt >= 17 or dt > 21:   # stand on 17+, stop if bust
            break

        # draw one card, recompute on next loo  p
        rank, card = random_card()
        game_state['dealer_hand'].append(card)

def simulate_player_cards(game_state):
    # Draw a random card
    rank, card = random_card()
    game_state['player_hand'].append(card)

    # Recompute total and soft/hard status after adding the card
    game_state['player_total'], _ = current_total_and_soft(game_state['player_hand'])

def deal_one_card_to_dealer(game_state):
    _, card = random_card()
    game_state['dealer_hand'].append(card)

def f_win(game_state):
    game_state['wins'] += 1
    game_state['balance'] += game_state['bet']
    game_state['bet'] = max(TABLE_MIN, min(game_state['balance'] * frac, TABLE_MAX))

def f_loss(game_state):
    game_state['losses'] += 1
    game_state['balance'] -= game_state['bet']
    game_state['bet'] = max(TABLE_MIN, min(game_state['balance'] * frac, TABLE_MAX))

def f_draw(game_state):
    game_state['draws'] += 1
    game_state['bet'] = max(TABLE_MIN, min(game_state['balance'] * frac, TABLE_MAX))

def is_blackjack(hand):
    if len(hand) != 2:
        return False
    ranks = [card.split(' of ')[0] for card in hand]
    return ('Ace' in ranks) and any(r in ('10', 'Jack', 'Queen', 'King') for r in ranks)

def fractional_checking(game_state):
    pt = game_state['player_total']
    dt = game_state['dealer_total']

    player_nat = is_blackjack(game_state['player_hand'])
    dealer_nat = is_blackjack(game_state['dealer_hand'])

    # Check naturals first
    if player_nat and dealer_nat:
        f_draw(game_state)
        return
    if player_nat:
        game_state['wins'] += 1
        game_state['balance'] += 1.5 * game_state['bet']
        game_state['bet'] = max(TABLE_MIN, min(game_state['balance'] * frac, TABLE_MAX))
        return
    if dealer_nat:
        f_loss(game_state)
        return

    # Player busts
    if pt > 21 and dt <= 21:
        f_loss(game_state)

    # Dealer busts
    elif dt > 21 and pt <= 21:
        f_win(game_state)

    # Normal comparison
    else:
        if pt > dt:
            f_win(game_state)
        elif pt < dt:
            f_loss(game_state)
        else:
            f_draw(game_state)

def fractional_strategy(game_state):
    # Reset for new round
    game_state['player_total'] = 0
    game_state['dealer_total'] = 0
    game_state['player_hand'] = []
    game_state['dealer_hand'] = []
    # Player gets two initial cards
    simulate_player_cards(game_state)
    simulate_player_cards(game_state)
    # Dealer gets two initial cards
    deal_one_card_to_dealer(game_state)
    deal_one_card_to_dealer(game_state)

    # Hard hands: stand on 17+ (no Ace or Ace counts as 1)
    # Soft hands: stand on 19+ (Ace counts as 11 without busting)
    while True:
        pt, soft = current_total_and_soft(game_state['player_hand'])
        game_state['player_total'] = pt

        # If hard total ≥17 → stand; if soft total ≥19 → stand
        if (not soft and pt >= 17) or (soft and pt >= 19):
            break
        simulate_player_cards(game_state)

    if game_state['player_total'] > 21:
        f_loss(game_state)
        return

    simulate_dealer_cards(game_state)

    game_state['player_total'], _ = current_total_and_soft(
        game_state['player_hand'])  # only computing the total, no need to know if soft or hard
    game_state['dealer_total'], _ = current_total_and_soft(game_state['dealer_hand'])
    fractional_checking(game_state)

#reset counters after every simulation
def reset(game_state):
    game_state['wins'] = 0
    game_state['losses'] = 0
    game_state['draws'] = 0

    game_state['balance'] = game_state['original_balance']
    game_state['bet'] = game_state['original_bet']


#def pickle_save(game_state):
    # Save wins, losses, draws, balance to pickle file
    #with open('f_stats.pkl', 'wb') as f:  # wb = write binary (for saving)
        #pickle.dump({'wins': game_state['wins'], 'losses': game_state['losses'], 'draws': game_state['draws'],
                     #'balance': game_state['balance']}, f)

    # print out stats after each successful game
    #print(
        #f"Wins: {game_state['wins']}, Losses: {game_state['losses']}, Draws: {game_state['draws']}, Balance: {game_state['balance']}")

#run automatic simulation of Blackjack
def fractional_run(game_state):
    global num_simulations, total_wins, total_losses, total_draws, total_ruin_counter
    reset(game_state)
    for i in range(num_simulations):
        session_balance = []
        session_bets = []
        session_stake = 0.0
        b0 = game_state['original_balance']  # starting bankroll for this session
        game_state['balance'] = min(game_state['original_balance'], BANKROLL_CAP)
        game_state['bet'] = max(TABLE_MIN, min(frac* game_state['balance'], TABLE_MAX))
        game_state['wins'] = 0
        game_state['losses'] = 0
        game_state['draws'] = 0
        game_state['ruin_counter'] = 0
        for j in range(hands_per_session):
         bet_used = game_state['bet']
         fractional_strategy(game_state)
         game_state['player_total'] = 0
         game_state['dealer_total'] = 0

         # End game when money runs out
         if game_state['balance'] < TABLE_MIN or game_state['bet'] > game_state['balance']:
            game_state['balance'] = max(game_state['balance'], 0)
            game_state['ruin_counter'] += 1
            #print('Not enough money!')
            break
         session_stake += bet_used

        # Add on each value of bets, bal    ance after each round
         bet_history.append(bet_used)
         session_bets.append(bet_used)  # per-session mean will use this
         balance_history.append(game_state['balance'])
         session_balance.append(game_state['balance'])  # per-session balance tracking

        if session_balance:  # avoid empty sessions
            peak = session_balance[0]
            trough = min(session_balance)
            dd = 1 - (trough / peak) if peak > 0 else 0.0
            max_drawdowns.append(dd)

        # pickle_save(game_state)

        total_wins += game_state['wins']
        total_losses += game_state['losses']
        total_draws += game_state['draws']
        total_ruin_counter += game_state['ruin_counter']

        final_balance = session_balance[-1] if session_balance else game_state['balance']
        session_returns.append(final_balance - b0)  # £ absolute return
        session_pct_returns.append((final_balance - b0) / b0)  # % return

        session_balance_history.append(final_balance)  # for plotting session-end balances

        session_bet_history.append(float(np.mean(session_bets)) if session_bets else 0.0)

        session_loss = b0 - final_balance

        # Loss per 100 units staked
        loss_per_100u = 100.0 * (session_loss / session_stake) if session_stake > 0 else 0.0
        loss_per_100u_list.append(loss_per_100u)

        # EV per hand (in units)
        ev_per_hand = (b0 - final_balance) / 100 / len(session_balance) if session_balance else 0.0
        ev_per_hand_list.append(ev_per_hand)

        #print('One session finished.')

fractional_run(game_state)

def ci_mean(x, z=1.96):
    x = np.asarray(x, float)
    m = x.mean()
    s = x.std(ddof=1)
    n = len(x)
    h = z * s / math.sqrt(n)
    return m - h, m + h
lo, hi = ci_mean(loss_per_100u_list)

session_pct_returns = np.array(session_pct_returns)

VaR_95 = np.percentile(session_pct_returns, 5)
CVaR_95 = session_pct_returns[session_pct_returns <= VaR_95].mean()

total_played_hands = total_wins + total_losses + total_draws
win_rate = total_wins / total_played_hands
loss_rate = total_losses / total_played_hands
average_bet = sum(bet_history) / len(bet_history)
mean_return = float(np.mean(session_pct_returns))            # fraction per session
standard_deviation_returns = float(np.std(session_pct_returns, ddof=1))
sharpe_ratio = mean_return / standard_deviation_returns if standard_deviation_returns > 0 else float('nan')
ruin_probability = total_ruin_counter / num_simulations

print(f"Config: min=1u, max=40u, bankroll=100u, hands/session=500")
print(f'Total simulations (of {hands_per_session} games): ', num_simulations)
print(f'Total complete games played: ',total_played_hands)
print("Bankroll: ", game_state['original_balance'])
print("Betting rule: Fixed-Fractional; base bet =", frac*game_state['original_balance'])
print(f'Win rate: {win_rate*100:.2f}%')
print(f'Loss rate: {loss_rate*100:.2f}%')
print(f'Average bet: {average_bet:.2f}')
print(f'Expected return per session: {mean_return*100:.2f}%')
print(f'Standard deviation of returns: {standard_deviation_returns*100:.2f}%')
print(f'Sharpe ratio: {sharpe_ratio:.3f}')
print(f'Ruin probability: {ruin_probability*100:.2f}%')
print(f"Average drawdown per session: {100*np.mean(max_drawdowns):.2f}%")
print(f"Average loss per 100u staked: {np.mean(loss_per_100u_list):.3f}u")
print(f"Average EV per hand: {np.mean(ev_per_hand_list):.4f}u")
print(f"95% CI (loss per 100u): [{lo:.3f}u, {hi:.3f}u]")
print(f"95% VaR: {VaR_95:.2%}")
print(f"95% CVaR (Expected Shortfall): {CVaR_95:.2%}")

#statistical analysis section

bets = np.asarray(session_bet_history) # change to NumPy array to compute rolling averages
balances = np.asarray(session_balance_history)

# Rolling average (smooth trend)
window = 1000  # rolling window size of 1000 simulations
kernel = np.ones(window) / window # list of numbers we use to average the last 1000 sessions
rolling = np.convolve(bets, kernel, mode='valid') # np.convolve() slides window across data and calculates the average for each position

plt.figure()
plt.plot(np.arange(window-1, window-1+rolling.size), rolling)
plt.title(f"Rolling Mean Bet – Fixed Fractional ({num_simulations} Sessions)")
plt.xlabel("Session #")
plt.ylabel("Bet Size (£)")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8,5))
plt.hist(balances, bins=200, density=False)
plt.title(f"Final Balance Distribution – Fixed Fractional ({num_simulations} Sessions)")
plt.xlabel("Final Balance (£)")
plt.ylabel("Count")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8,5))
plt.hist(session_pct_returns, bins=50, density=True, alpha=0.75)
plt.xlabel("Simple return per session")
plt.ylabel("Probability density")
plt.title(f"Return Distribution Per Session – Fixed Fractional Betting")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
