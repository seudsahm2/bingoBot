import random

bingo_sessions = {}

class BingoGame:
    def __init__(self):
        # user_id -> card (2D list of numbers)
        self.players = {}

        # user_id -> {"card": 2D list, "self_marks": set, "enemy_marks": set}
        self.player_cards = {}

        self.turn_order = []  # player turn order
        self.current_turn_index = 0  # whose turn
        self.completed_lines = {}  # user_id -> completed lines (for BINGO)
        self.line_mark_letters = ['B', 'I', 'N', 'G', 'O']
        self.called_numbers = set()  # ✅ required to track already picked numbers
        self.mark_symbols = {}  # user_id -> symbol for marking (e.g. colored circle)
        self.game_over = False  # flag to indicate if game is over

    def generate_card(self):
        # Generate a 5x5 bingo card with unique random numbers from 1 to 25
        nums = random.sample(range(1, 26), 25)
        card = [nums[i * 5:(i + 1) * 5] for i in range(5)]
        return card

    def add_player(self, user_id):
        if user_id in self.players:
            return False  # player already in game

        card = self.generate_card()
        self.players[user_id] = card

        self.player_cards[user_id] = {
            "card": card,
            "self_marks": set(),  # player's own picks
            "enemy_marks": set(),  # others' picks that affect this card
        }

        default_symbols = ["🔵", "🟡", "🔴", "🟢", "🟣", "🟠"]
        self.mark_symbols[user_id] = default_symbols[len(self.mark_symbols) % len(default_symbols)]
        self.completed_lines[user_id] = []
        
            # ✅ Setup turn order once 2 players have joined
        if len(self.players) == 2:
            self.turn_order = list(self.players.keys())
            self.current_turn_index = 0  # start from first player

        return True

    def get_current_player(self):
        # Return current player whose turn it is
        if not self.turn_order:
            return None
        return self.turn_order[self.current_turn_index]

    def next_turn(self):
        # Advance to next player's turn
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def submit_number(self, user_id, number):
        # ✅ If game is over, block further action
        if self.game_over:
            return False, "❌ Game is already over.", False
        # Check turn validity
        if self.get_current_player() != user_id:
            return False, "It's not your turn.", False

        # Number must exist in caller's own card
        if number not in [cell for row in self.players[user_id] for cell in row]:
            return False, "Number not on your card.", False

        if number in self.called_numbers:
            return False, "Number already called.", False

        # Add to global called numbers set
        self.called_numbers.add(number)

        # ✅ Mark number on each player's card
        for pid, pdata in self.player_cards.items():
            card = pdata["card"]
            for r in range(5):
                for c in range(5):
                    if card[r][c] == number:
                        card[r][c] = self.mark_symbols[pid]
                        if pid == user_id:
                            pdata["self_marks"].add(self.mark_symbols[pid])
                        else:
                            pdata["enemy_marks"].add(self.mark_symbols[pid])

        # ✅ Check win only for the current player
        won = self.check_winner(user_id)
        # ✅ If player won, mark game as over
        if won:
            self.game_over = True
            return True, f"Number {number:02} marked. BINGO! 🎉", True

        # Next player's turn
        self.next_turn()

        return True, f"Number {number:02} marked on all cards.", False


    def check_winner(self, user_id):
        """
        Checks rows, cols, and diagonals to track completed lines.
        A line is complete if all its numbers are in self_marks or enemy_marks.
        Only self_marks count toward BINGO.
        """
        pdata = self.player_cards[user_id]
        card = pdata["card"]
        marks = pdata["self_marks"]  # only own marks count

        completed = self.completed_lines[user_id]

        # Check rows
        for r in range(5):
            if all(card[r][c] in marks for c in range(5)) and f"row{r}" not in completed:
                completed.append(f"row{r}")

        # Check columns
        for c in range(5):
            if all(card[r][c] in marks for r in range(5)) and f"col{c}" not in completed:
                completed.append(f"col{c}")

        # Check diagonals
        if all(card[i][i] in marks for i in range(5)) and "diag1" not in completed:
            completed.append("diag1")
        if all(card[i][4 - i] in marks for i in range(5)) and "diag2" not in completed:
            completed.append("diag2")
        return len(completed) >= 5  # BINGO if 5 or more lines completed

    def get_card_text(self, user_id):
        """
        Renders a user's card with:
        🔵 for their own picks,
        🟡 for enemy picks,
        numbers otherwise.
        Shows BINGO progress.
        """
        if user_id not in self.player_cards:
            return "You don't have a card yet."

        card = self.player_cards[user_id]["card"]
        self_marks = self.player_cards[user_id]["self_marks"]
        enemy_marks = self.player_cards[user_id]["enemy_marks"]
        progress = self.line_mark_letters[:len(self.completed_lines[user_id])]

        header = " B  I  N  G  O\n"
        rows = []
        for r in range(5):
            row_str = ""
            for c in range(5):
                num = card[r][c]
                if num in self_marks:
                    row_str += "🔵 "
                elif num in enemy_marks:
                    row_str += "🟡 "
                elif isinstance(num, int):
                    row_str += f"{num:02} "
                else:
                    row_str += "?? "
            rows.append(row_str.strip())

        return header + "\n".join(rows) + f"\n\nProgress: {''.join(progress)}"
