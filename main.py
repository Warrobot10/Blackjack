import typer
import random
from typing_extensions import Annotated

app = typer.Typer()

allowed_num_decks = [2, 4, 8]

def generate_decks(decks: int):
    if decks in allowed_num_decks:
        # Each deck contains cards from 1 to 13 (representing 13 card types)
        return [card for card in range(1, 14)] * decks
    else:
        print("Invalid number of decks, either 2, 4 or 8.")
        raise typer.Abort()

def init_decks(decks: int):
    # Initialize a deck of cards (with a valid number of decks)
    deck = generate_decks(decks)
    random.seed() # Seed the Random-Number-Generator
    random.shuffle(deck)  # Shuffle the deck for randomness
    print(f"A deck with {decks} decks initialized and shuffled:")

def deal(decks: int):
    print(random.choice(deck))

@app.command()
def play(decks: Annotated[int, typer.Argument(help="The number of decks you will play: 2, 4 or 8.")]):
    init_decks(decks)
    deal(decks)

if __name__ == "__main__":
    app()