import random
import json
import time
import typer
from typing_extensions import Annotated

app = typer.Typer()

allowed_num_decks = [2, 4, 8]

def generate_decks(decks: int):
    if decks in allowed_num_decks:
        return [card for card in range(1, 14)] * decks
    else:
        print("Invalid number of decks, must be one of: 2, 4, or 8.")
        raise typer.Abort()

def init_decks(decks: int):
    deck = generate_decks(decks)
    random.shuffle(deck)
    return deck

def deal_card(deck: list):
    if len(deck) == 0:
        return None, deck
    card = random.choice(deck)
    deck.remove(card)
    return card, deck

def get_card_value(hand: list):
    total = 0
    aces = 0

    for card in hand:
        if card >= 10:
            total += 10
        elif card == 1:
            aces += 1
        else:
            total += card

    for _ in range(aces):
        if total + 11 <= 21:
            total += 11
        else:
            total += 1

    return total

def play_round(decks: int, strategy: dict, wager: int, player_balance: int):
    deck = init_decks(decks)
    player_hand = []
    dealer_hand = []

    # Initial deal
    for _ in range(2):
        card, deck = deal_card(deck)
        player_hand.append(card)

        card, deck = deal_card(deck)
        dealer_hand.append(card)

    print(f"Your hand: {player_hand}")
    print(f"Dealer's hand: [X, {dealer_hand[1]}]")

    # Insurance option
    insurance_bet = 0
    if dealer_hand[0] == 1:
        if strategy.get("insurance", False):
            insurance_bet = wager / 2
            print(f"You've placed an insurance bet of ${insurance_bet}")

    player_busted = False
    player_total = get_card_value(player_hand)
    # The player's strategy is to keep drawing until they reach the target value (based on the config)
    while player_total < strategy.get("player_stand_value", 17):
        card, deck = deal_card(deck)
        player_hand.append(card)
        player_total = get_card_value(player_hand)
        print(f"You drew: {card}. Your hand: {player_hand} (Total value: {player_total})")

        if player_total > 21:
            print("You busted! Dealer wins this round.")
            player_balance -= wager
            player_busted = True
            break

    if not player_busted:
        print(f"Your final hand: {player_hand} (Total value: {player_total})")
        print(f"Dealer's hand: {dealer_hand}")

        # Dealer's strategy to draw until they reach the target value (based on the config)
        dealer_total = get_card_value(dealer_hand)
        while dealer_total < strategy.get("dealer_stand_value", 17):
            card, deck = deal_card(deck)
            dealer_hand.append(card)
            dealer_total = get_card_value(dealer_hand)
            print(f"Dealer drew: {card}. Dealer's hand: {dealer_hand} (Total value: {dealer_total})")

        print(f"Dealer's final hand: {dealer_hand} (Total value: {dealer_total})")

        if dealer_total > 21:
            print("Dealer busted! You win!")
            player_balance += wager
        elif player_total > dealer_total:
            print("You win!")
            player_balance += wager
        elif player_total < dealer_total:
            print("Dealer wins.")
            player_balance -= wager
        else:
            print("It's a tie!")

        # Insurance payout check
        if insurance_bet > 0 and dealer_total == 21:
            print("Dealer has Blackjack! You win the insurance bet!")
            player_balance += insurance_bet
        elif insurance_bet > 0:
            print("Dealer does not have Blackjack. You lose the insurance bet.")
            player_balance -= insurance_bet

    return player_balance


def simulate_game(decks: int, strategy: dict, wager: int, player_balance: int):
    """
    Simulate a game of blackjack and return updated balance and game result.
    """
    player_balance = play_round(decks, strategy, wager, player_balance)

    return player_balance, player_balance > 0, player_balance - strategy['player_balance'], False


@app.command()
def simulate(
    strategy_file: str = typer.Option("strategy.json", help="JSON file containing strategies and configuration."),
    simulate: int = typer.Option(0, help="Number of games to simulate."),
):
    """
    Simulate a series of blackjack games with customizable strategies.
    """
    # Load the strategy file
    with open(strategy_file, "r") as f:
        strategy = json.load(f)

    player_balance = strategy.get("player_balance", 100)
    decks = strategy.get("decks", 4)
    wager = strategy.get("wager", 10)
    total_games = simulate
    player_stand_value = strategy.get("player_stand_value", 17)
    dealer_stand_value = strategy.get("dealer_stand_value", 17)

    game_wins = 0
    game_losses = 0
    game_ties = 0
    total_bets = 0
    total_winnings_lost = 0  # Track net winnings or losses

    start_time = time.time()

    # Run the simulation until the specified number of games is reached
    rounds_played = 0
    while rounds_played < total_games and player_balance > 0:
        deck = generate_decks(decks)
        random.shuffle(deck)

        print(f"\nCurrent balance: {player_balance}")
        total_bets += wager

        # If player doesn't have enough balance to continue, exit simulation
        if player_balance < wager:
            print(f"Player doesn't have enough balance to continue. Ending simulation.")
            break

        # Play round
        player_balance, game_won, net_winnings_lost, is_blackjack = simulate_game(decks, strategy, wager, player_balance)
        rounds_played += 1
        if game_won:
            game_wins += 1
        elif game_won is False:
            game_losses += 1
        else:
            game_ties += 1

        total_winnings_lost += net_winnings_lost

    end_time = time.time()
    total_time = end_time - start_time
    average_win_percentage = (game_wins / rounds_played) * 100 if rounds_played > 0 else 0
    time_per_game = total_time / rounds_played if rounds_played > 0 else 0

    # Output the simulation results
    print(f"\nSimulation Results:")
    print(f"Total games played: {rounds_played}")
    print(f"Games won: {game_wins} ({average_win_percentage:.2f}%)")
    print(f"Games lost: {game_losses}")
    print(f"Ties: {game_ties}")
    print(f"Time taken: {total_time:.2f} seconds")
    print(f"Average time per game: {time_per_game:.2f} seconds")
    print(f"Total wagered: ${total_bets:.2f}")
    print(f"Total winnings/losses: ${total_winnings_lost:.2f}")
    print(f"Final balance: ${player_balance:.2f}")


if __name__ == "__main__":
    app()
