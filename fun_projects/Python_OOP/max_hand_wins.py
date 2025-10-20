import random
import time
from enum import Enum
from functools import total_ordering

class Suit(Enum):
    SPADES = 4
    HEARTS = 3
    DIAMONDS = 2
    CLUBS = 1


@total_ordering
class PlayingCard:
    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    def get_rank(self):
        return self._rank

    def get_suit(self):
        return self._suit

    def __eq__(self, p):
        return (self._rank == p._rank and self._suit == p._suit)

    def __gt__(self, p):
        if self._rank > p._rank:
            return True
        if self._rank == p._rank:
            return self._suit.value > p._suit.value
        return False

    def __str__(self):
        return f'({self.get_rank()}, {self.get_suit().name})'

            


class Player:
    def __init__(self, name):
        self._name = name
        self._hand = []

    def get_name(self):
        return self._name

    def get_hand(self):
        return self._hand

    def set_hand(self, hand):
        self._hand = hand

    def strongest_card(self):
        if len(self._hand) == 2:
            return max(self._hand)

class Deck:
    def __init__(self):
        self._cards = []
        for i in range(13):
            self._cards.append(PlayingCard(i+2, Suit.SPADES))
            self._cards.append(PlayingCard(i+2, Suit.DIAMONDS))
            self._cards.append(PlayingCard(i+2, Suit.HEARTS))
            self._cards.append(PlayingCard(i+2, Suit.CLUBS))
    
    def get_cards(self):
        return self._cards

    def shuffle_cards(self):
        random.shuffle(self._cards)

    def draw(self, n):
        if len(self._cards) >= n:
            drawn = []
            for i in range(n):
                drawn.append(self._cards.pop())
            return drawn
        else:
            return None

    def draw2(self, n):
        if len(self._cards) >= n:
            drawn = self._cards[-n:]
            for i in range(n):
                del self._cards[len(self._cards) - 1]
            return drawn
        else:
            return None

class Game:
    def __init__(self, players, deck):
        self._players = players # a list of all players participating in the game
        self._deck = deck # an instance of the Deck class that we created previously
        self._score = {} # to keep the score of how many rounds each player won
        for p in players:
            self._score[p.get_name()] = 0 # initialize the scores to zeroes

    def _show_score(self):
        """prints the scores of all players on the screen"""
        print("Score:")
        print("-----")
        for k, v in self._score.items():
            print(f'{k}: {v}')
        print('\n')

    def _is_more_rounds(self):
        """just a helper function that indicated if there are more rounds remaining"""
        return len(self._deck.get_cards()) >= 2 * len(self._players)
    
    def _play_round(self):
        """simulates going through one round of the game
        
        - Each player draws two cards from the deck.
        - Each player shows the strongest card in his hand, the player with the strongest card overall wins the round.
        - The scoreboard is updated."""
        
        winning_card = None
        winning_player = None
        for p in self._players:
            hand = self._deck.draw(2)
            p.set_hand(hand)
            print(f'player {p.get_name()} is dealt: [{hand[0]},{hand[1]}]')
            if winning_card is None or (
                p.strongest_card().get_rank() > winning_card.get_rank()
                ) or (
                (p.strongest_card().get_rank() == winning_card.get_rank()) 
                and (p.strongest_card().get_suit().value > winning_card.get_suit().value)
                ):
                winning_card = p.strongest_card()
                winning_player = p

        print(f'PLAYER {winning_player.get_name()} WINS THIS ROUND\n')
        self._score[winning_player.get_name()] += 1
        self._show_score()
        time.sleep(6)


    def play(self):
        while self._is_more_rounds():
            self._play_round()
        winner = max(self._score, key=self._score.get)
        print(f'\n\nPlayer {winner} won the game')



class Cheater(Player):
    """The Cheater is a special player who, when asked to show the strongest card in his hand, can
    show an Ace of Spades (the strongest card in the game) with a ​ 20% chance​ ."""
    def strongest_card(self):
        # return ace of spades with 20% chance
        if random.randint(1, 10) <= 2:
            return PlayingCard(14, Suit.SPADES)
        else:
            return super().strongest_card()



if __name__ == '__main__':
    p1 = Player('Alice')
    p2 = Player('Bob')
    p3 = Cheater('Andrii')

d = Deck()
d.shuffle_cards()

g = Game([p1, p2, p3], d)
g.play()
