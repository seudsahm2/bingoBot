import random

bingo_sessions = {}
class BingoGame:
    def __init__(self):
        self.players = {}  # user_id -> player's card (2D list)
        self.turn_order = []  # list of user_ids in turn order
        self.current_turn_index = 0  # index of who's turn it is
        self.called_numbers = set()  # numbers that have been called (marked by any player)
        self.mark_symbols = {}  # user_id -> symbol to mark their called numbers
        self.completed_lines = {}  # user_id -> list of completed lines identifiers
        self.line_mark_letters = ['B', 'I', 'N', 'G', 'O']  # 5 possible lines for Bingo
        
    def generate_card(self):
        nums = random.sample(range(1, 26), 25)
        card = [nums[i * 5:(i + 1) * 5] for i in range(5)]
        return card
    
    def get_card_text(self, user_id):
        """
        Returns a formatted string representing the player's card,
        with columns labeled B I N G O and showing numbers or marked symbols.
        """

        if user_id not in self.players:
            return "You don't have a card yet."

        card = self.players[user_id]

        # Header row for Bingo columns
        header = " B  I  N  G  O\n"

        # Each row of the card
        rows_text = []
        for row in card:
            row_str = ""
            for cell in row:
                # cell could be a number (int) or a mark symbol / letter (str)
                if isinstance(cell, int):
                    # Format numbers with leading spaces for alignment
                    row_str += f"{cell:2d} "
                else:
                    # For symbols or letters, just print them with a space
                    row_str += f"{cell}  "
            rows_text.append(row_str.rstrip())

        # Combine header and rows
        card_text = header + "\n".join(rows_text)
        return card_text

    def add_player(self, user_id):
        if user_id in self.players:
            return False  # already joined
        card = self.generate_card()
        self.players[user_id] = card
        self.turn_order.append(user_id)
        self.mark_symbols[user_id] = chr(0x1F7E6 + len(self.mark_symbols))  # 🟦🟩🟨🟧🟥 (colored squares)
        return True

    def get_current_player(self):
        if not self.turn_order:
            return None
        return self.turn_order[self.current_turn_index]

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def submit_number(self, user_id, number):
        # Check if it's this user's turn
        if self.get_current_player() != user_id:
            return False, "It's not your turn.", False

        if number not in [num for row in self.players[user_id] for num in row]:
            return False, "Number not on your card.", False

        if number in self.called_numbers:
            return False, "Number already called.", False


        # Mark the number for all players on their cards
        symbol = self.mark_symbols[user_id]
        for pid, card in self.players.items():
            for r in range(5):
                for c in range(5):
                    if card[r][c] == number:
                        card[r][c] = symbol

        # Add number to called numbers
        self.called_numbers.add(number)
        
        # Check if this player won
        won = self.check_winner(user_id)

        # Move to next turn
        self.next_turn()

        return True, f"Number {number:02} marked for player.",won

    # You can add more methods for checking win, formatting cards, etc.
    def check_winner(self, user_id):
        """
        Check if the user completed any new row, column or diagonal.
        Mark the new lines on the card with the respective letter.
        Return True if the user has won (5 lines completed).
        """

        card = self.players[user_id]
        if user_id not in self.completed_lines:
            self.completed_lines[user_id] = []

        new_completed = []

        # Helper to check if a line is fully marked (only symbols or letters, no numbers)
        def line_completed(cells):
            # For our game, a cell is either a symbol (str) or a number (int)
            # A line is complete if no cell is int (numbers), i.e. all replaced
            return all(isinstance(x, str) for x in cells)

        # Check rows
        for r in range(5):
            if ('row', r) not in self.completed_lines[user_id]:
                if line_completed(card[r]):
                    new_completed.append(('row', r))

        # Check columns
        for c in range(5):
            col = [card[r][c] for r in range(5)]
            if ('col', c) not in self.completed_lines[user_id]:
                if line_completed(col):
                    new_completed.append(('col', c))

        # Check diagonals
        diag1 = [card[i][i] for i in range(5)]
        if ('diag', 1) not in self.completed_lines[user_id]:
            if line_completed(diag1):
                new_completed.append(('diag', 1))

        diag2 = [card[i][4 - i] for i in range(5)]
        if ('diag', 2) not in self.completed_lines[user_id]:
            if line_completed(diag2):
                new_completed.append(('diag', 2))

        # For each new completed line, mark it on the card with the letter
        for line in new_completed:
            if len(self.completed_lines[user_id]) < 5:
                letter = self.line_mark_letters[len(self.completed_lines[user_id])]
                self.completed_lines[user_id].append(line)
                # Mark the entire line with this letter
                if line[0] == 'row':
                    r = line[1]
                    for c in range(5):
                        card[r][c] = letter
                elif line[0] == 'col':
                    c = line[1]
                    for r in range(5):
                        card[r][c] = letter
                elif line[0] == 'diag':
                    if line[1] == 1:
                        for i in range(5):
                            card[i][i] = letter
                    elif line[1] == 2:
                        for i in range(5):
                            card[i][4 - i] = letter

        # Return True if player completed all 5 lines (i.e., BINGO)
        return len(self.completed_lines[user_id]) == 5