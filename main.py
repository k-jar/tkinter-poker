import random  # Allows for randomness
import tkinter as tk  # Tkinter used for gui
# import mysql.connector  # Used for database
from PIL import Image, ImageTk
import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('localdatabase.db') 
        
        # Create a cursor object
        mycursor = conn.cursor()
        
        # Create table
        mycursor.execute('''
            CREATE TABLE users (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                win_num INTEGER DEFAULT 0,
                bust_num INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                money INTEGER DEFAULT 1000
            )
        ''')
        
    except Error as e:
        print(e)
    finally:
        return mycursor, conn

mycursor, conn = create_connection()

# for x in myresult:
#   print(x)

########
# GAME #
########


# Defining class for the game, contains functions to get cards and check for wins
class pokerGame:
    # All cards list
    cards = [
        ["01S", "02S", "03S", "04S", "05S", "06S", "07S", "08S", "09S", "10S", "11S", "12S", "13S"],
        ["01H", "02H", "03H", "04H", "05H", "06H", "07H", "08H", "09H", "10H", "11H", "12H", "13H"],
        ["01C", "02C", "03C", "04C", "05C", "06C", "07C", "08C", "09C", "10C", "11C", "12C", "13C"],
        ["01D", "02D", "03D", "04D", "05D", "06D", "07D", "08D", "09D", "10D", "11D", "12D", "13D"]
    ]
    # Community card list
    com_cards = []
    # Number of current round
    round_num = 1
    # Dictionary for determining hand rank
    hand_rank_dict = {
        1: "High card",
        2: "One pair",
        3: "Two pair",
        4: "Three of a kind",
        5: "Straight",
        6: "Flush",
        7: "Full house",
        8: "Four of a kind",
        9: "Straight flush"
    }

    # List containing all players
    player_list = []

    # List for players during a game
    active_player_list = []

    # Attribute to hold the winning player
    winner = None

    # Attribute to hold community card images
    com_images = []

    # Money in pot
    pot = 0

    # Do not reset
    # Attribute to hold dealer
    dealer = None

    # Attributes for players betting blinds
    small_blind = None
    big_blind = None

    # Attributes for the amount that needs to be bet for blinds
    small_blind_amount = 5
    big_blind_amount = 10

    # Minimum bet attribute, initially this is equal to the big blind
    bet_to_match = big_blind_amount

    # Minimum raise attribute, initially big blind
    min_raise = big_blind_amount
    # Maximum raise attribute
    max_bet = 100

    # Attribute for the current player's turn
    current_turn = None
    # Attribute for the first player to act
    starting_player = None

    # Attribute used to check if every player has acted
    players_acted = 0

    # Attribute for if there is a draw
    draw = False

    # Creates a player instance
    def __init__(self, setPlayer):
        # Setting player number
        self.player_num = setPlayer
        # List for player's cards
        self.p_cards = []
        # List for player's and community cards
        self.p_and_com = []
        # List for player's and community cards with 14s appended if there are aces
        self.p_and_com_ace = []
        # List for matching value cards in a player possible hand
        self.matches = None
        # Attribute for the type of matching cards the player has
        self.match_type = None
        # Attribute for the full match hand which includes kickers
        self.match_hand = []
        # Attributes for cards making up hands for each hand type
        self.straight = []
        self.flush = []
        self.full_house = []
        self.straight_flush = []
        # Attribute for the best hand the player has
        self.best_hand = []
        # Attribute to hold the player's hand rank
        self.hand_rank = None
        # Attribute to hold the player's money
        self.money = 1000
        # Attribute to check if this player is the dealer
        self.dealer = False
        # Attribute for the players total bet in the current game
        self.current_bet = 0

        # Attribute for some widgets pertaining to this player
        self.widgets = []
        # Attribute to check if the player has folded
        self.fold_status = False
        # Attribute to check if the player has raised
        self.raised = False
        # Attribute containing all the actions a player can make
        self.action_list = [self.fold, self.check_call, self.raise_bet]

        # Attribute for the card images for this player
        self.p_imgs = []

        # Assigns different placeholder objects depending on player number
        if self.player_num == 1:
            self.placeholders = [p1_ph1, p1_ph2]
        elif self.player_num == 2:
            self.placeholders = [p2_ph1, p2_ph2]
        elif self.player_num == 3:
            self.placeholders = [p3_ph1, p3_ph2]
        elif self.player_num == 4:
            self.placeholders = [p4_ph1, p4_ph2]
        elif self.player_num == 5:
            self.placeholders = [p5_ph1, p5_ph2]

    # Method to generate random cards
    @staticmethod
    def gen_card():
        # Picking a random suit
        rand_suit = random.choice(pokerGame.cards)
        # Picking a random card
        rand_card = random.choice(rand_suit)
        # Removes the card picked to prevent repeats
        rand_suit.remove(rand_card)
        # Returns the random card
        return rand_card

    # # Method to give players 2 cards
    # @classmethod
    # def give_p_cards(cls):
    #     for i in range(len(cls.player_list)):
    #         player = cls.player_list[i]
    #         for y in range(2):
    #             # appends random cards to player hand
    #             player.p_cards.append(player.gen_card())
    #         player.display_p_cards()
    #         player.hand_check()

    # Method to give players 2 cards
    @classmethod
    def give_p_cards(cls):
        for player in cls.player_list:
            for y in range(2):
                # Appends random cards to player hand
                player.p_cards.append(player.gen_card())
                # Checking what the player's best hand is
                player.hand_check()
        # Displaying player's cards
        cls.player_list[0].display_p_cards()

    # Method to display player cards
    def display_p_cards(self):
        # Changing card image size depending on player
        if self.player_num == 1:
            self.display_cards(range(2), self.p_imgs, self.p_cards, self.placeholders, (165, 240))
        else:
            self.display_cards(range(2), self.p_imgs, self.p_cards, self.placeholders, (84, 120))

    # Method to display cards
    @staticmethod
    def display_cards(set_range, set_image_list, set_cards, set_placeholders, img_size):
        for i in set_range:
            # Opening the card image located in the card_png folder
            tempImg = Image.open("card_png/" + set_cards[i] + ".png")
            # Resizing the image depending on the given img_size parameter
            tempImg = tempImg.resize(img_size)
            # Appending the card image to the given list
            set_image_list.append(ImageTk.PhotoImage(tempImg))
            # Changing the placeholder images to the card images
            set_placeholders[i].config(image=set_image_list[i])

    # Method to create 5 players
    @classmethod
    def create_players(cls):
        # Initialising all player variables
        player1 = player2 = player3 = player4 = player5 = None
        # Storing these variables in the player_list class variable
        cls.player_list = [player1, player2, player3, player4, player5]
        # Going through each element of the list and turning them into pokerGame objects
        for i in range(len(cls.player_list)):
            cls.player_list[i] = cls(i + 1)
        # Creating a copy of the player_list to be used for the win_check method later
        cls.active_player_list = cls.player_list.copy()

        cls.player_list[0].money = user_money

        cls.player_list[0].widgets.extend([label_p1_act, label_p1_info])
        cls.player_list[1].widgets.extend([label_p2_act, label_p2_info])
        cls.player_list[2].widgets.extend([label_p3_act, label_p3_info])
        cls.player_list[3].widgets.extend([label_p4_act, label_p4_info])
        cls.player_list[4].widgets.extend([label_p5_act, label_p5_info])

    # Function to start the game
    @classmethod
    def start(cls):
        # Hiding the menu frame and showing the game frame
        frame_menu.grid_forget()
        frame_game.grid()
        # Changing the play button to a resume button
        button_play.config(text="Resume", command=resume)
        # Creating players
        cls.create_players()
        cls.new_game()

    @classmethod
    def new_game(cls):
        # Configuring the action buttons so they call the action methods
        button_fold.config(command=pokerGame.player_list[0].fold)
        button_check_call.config(command=pokerGame.player_list[0].check_call)
        # For the raise method a parameter for the raise amount is passed in.
        # This parameter is the result of a function getting the value from the slider for raising.
        button_raise.config(command=lambda: pokerGame.player_list[0].raise_bet(slider_raise.get()))

        label_round.config(text="Round 1")

        # Giving players cards
        cls.give_p_cards()
        # Setting the dealer and the players that need to bet blinds
        cls.set_dealer_blinds()
        # Updating widgets displaying player information
        cls.update_gui()
        # Allowing the first player to act
        cls.player_action()

    # Method to set the dealer and players that need to bet blinds
    @classmethod
    def set_dealer_blinds(cls):
        # Declaring variable for length of player_list
        player_list_len = len(cls.player_list)
        # Chooses a random dealer if there is no dealer currently
        if cls.dealer is None:
            cls.dealer = random.choice(cls.player_list)

        # Variable to hold index of dealer player
        dealer_location = cls.dealer.player_num - 1
        # If the current dealer is the last player then the next dealer is the first player
        if cls.dealer.player_num == player_list_len:
            cls.dealer = cls.player_list[0]
            dealer_location = 0
        # Otherwise, just make the following player the dealer
        else:
            dealer_location += 1
            cls.dealer = cls.player_list[dealer_location]
        # Setting the players betting blinds
        print("dealer loc", dealer_location)
        small_blind_num = dealer_location + 1
        print("small blind num2", small_blind_num)
        big_blind_num = dealer_location + 2
        starting_player_num = dealer_location + 3
        # If chosen player is after the last player then return to the first player
        if small_blind_num > player_list_len - 1:
            small_blind_num = 0
        if big_blind_num > player_list_len - 1:
            big_blind_num = big_blind_num - player_list_len
        if starting_player_num > player_list_len - 1:
            starting_player_num = starting_player_num - player_list_len

        # Storing players betting blinds in class attributes
        cls.small_blind = cls.player_list[small_blind_num]
        cls.big_blind = cls.player_list[big_blind_num]

        # Storing the starting player in two attributes, current_turn will keep track of current player.
        # Starting_player will be just be used to hold the starting player.
        cls.current_turn = cls.starting_player = cls.player_list[starting_player_num]

        # Subtracting the amount of the small blind from the player betting it
        cls.small_blind.money = cls.small_blind.money - cls.small_blind_amount
        # Changing this player's current bet to the small blind amount
        cls.small_blind.current_bet = cls.small_blind_amount
        # Doing the same for the big blind
        cls.big_blind.money = cls.big_blind.money - cls.big_blind_amount
        cls.big_blind.current_bet = cls.big_blind_amount

        # Adding the small blind and big blind to the pot
        cls.pot = cls.pot + cls.small_blind_amount + cls.big_blind_amount

        # If the starting player is the user then enable all the action buttons
        if cls.current_turn.player_num == 1:
            button_fold.config(state="active")
            button_check_call.config(state="active")
            button_raise.config(state="active")

    # Method to update widgets
    @classmethod
    def update_gui(cls):
        # Updating player information widgets
        for player in cls.player_list:
            widget_text = ("$" + str(player.money))
            # Also, updating hand type for player 1
            if player.player_num == 1:
                widget_text = widget_text + "\n" + cls.hand_rank_dict[player.hand_rank]
            if player == cls.dealer:
                widget_text = "Dealer\n" + widget_text
            elif player == cls.small_blind:
                widget_text = "Small blind\n" + widget_text
            elif player == cls.big_blind:
                widget_text = "Big blind\n" + widget_text
            player.widgets[1].config(text=widget_text)

        # Updating pot amount
        label_pot.config(text="Pot = $" + str(cls.pot))

        # Updating turn label
        label_turn.config(text="Player " + str(cls.current_turn.player_num) + "'s Turn")

    # Method used to fold, forfeit the player from the current game
    def fold(self, action_text="Fold"):
        # Configuring the player's action widget to show their decision
        self.widgets[0].config(text=action_text)
        # Setting player's fold attribute to true
        self.fold_status = True
        # Removing the player from the player list for players still in the game
        pokerGame.active_player_list.remove(self)

        # Changing the card images, the size depends on the player
        if self.player_num == 1:
            temp_back_img = blank_back
            # Also, disabling action buttons
            button_fold.config(state="disabled")
            button_check_call.config(state="disabled")
            button_raise.config(state="disabled")
        else:
            temp_back_img = blank_back_small
        for i in range(2):
            self.placeholders[i].config(image=temp_back_img)

        # Progressing to the next turn
        pokerGame.next_turn()

    # Method used to check or call
    def check_call(self):
        # If the player's current bet is less than the highest bet then call
        if self.current_bet < pokerGame.bet_to_match:
            difference = self.bet_to_match - self.current_bet
            self.widgets[0].config(text="Call $" + str(difference))
            # Bets the amount needed to match the highest bet.
            # Calls the bet method with the amount parameter passed in.
            self.bet(difference)
        # Otherwise, the player checks, essentially doing nothing
        else:
            self.widgets[0].config(text="Check")

        # Updating widgets
        self.update_gui()
        # Progressing to the next turn
        pokerGame.next_turn()

    # Method for raising with a parameter for the raise amount
    def raise_bet(self, raise_amount):
        # label_act.config(text="RAISE")
        # if self.player_num == 1:
        #     raise_amount = slider_raise.get()
        # else:
        #     raise_amount = 20

        # If the player's current bet is less than the highest bet then add the difference to raise_amount
        if self.current_bet < pokerGame.bet_to_match:
            total_bet = raise_amount + (self.bet_to_match - self.current_bet)
        # Otherwise, just use the raise_amount
        else:
            total_bet = raise_amount
        # Setting the minimum raise to the current raise
        pokerGame.min_raise = raise_amount
        # The raise amount is added to the current bet_to_match
        pokerGame.bet_to_match = pokerGame.bet_to_match + raise_amount
        # Calling the bet method
        self.bet(total_bet)
        # Configuring the player's action widget to show their decision
        self.widgets[0].config(text="Raise $" + str(raise_amount))
        # Setting the player raised attribute to True
        self.raised = True
        # Resetting the players_acted class attribute to allow every player to act again
        pokerGame.players_acted = 0
        # Progressing to the next turn
        pokerGame.next_turn()

    # Method used to bet, move money from the player to the pot
    def bet(self, amount):
        # Subtracting the amount bet from the player's money attribute
        self.money = self.money - amount
        if self.money <= 0:
            self.fold("Bust")
        # Adding this amount to the players current bet
        self.current_bet = self.current_bet + amount
        # Also, adding this amount to the pot
        pokerGame.pot = pokerGame.pot + amount
        # Updating widgets
        self.update_gui()

    # Method used to determine if the current player is the user or computer and allow them both to act
    @classmethod
    def player_action(cls):
        # If the current player is the user then enable the action buttons
        if cls.current_turn.player_num == 1:
            # Changes check/call button text depending on if the player's bet matches the highest bet
            if cls.current_turn.current_bet != cls.bet_to_match:
                button_check_call.config(text="Call")
            else:
                button_check_call.config(text="Check")

            # Changing the limits of the slider widget to the minimum and maximum raise amounts
            max_bet = cls.max_bet
            # Prevents user from raising more than they can
            if cls.current_turn.money < max_bet:
                max_bet = cls.current_turn.money
            slider_raise.config(to=cls.min_raise, from_=max_bet)

            # Check to prevent the player from raising if they have already raised
            if cls.current_turn.raised:
                button_raise.config(state="disabled")
            else:
                button_raise.config(state="active")

            button_fold.config(state="active")
            button_check_call.config(state="active")

        # Otherwise, call the bot decision-making method
        else:
            button_fold.config(state="disabled")
            button_check_call.config(state="disabled")
            button_raise.config(state="disabled")
            cls.current_turn.smarter_bot_ai()

    # Method that randomly chooses actions for the bot to take
    def random_bot_ai(self):
        chosen_action = random.choice(self.action_list)
        # Passes raise amount parameter if chosen action is to raise
        if chosen_action == self.raise_bet:
            raise_amount = random.randrange(pokerGame.min_raise, pokerGame.max_bet, 5)
            chosen_action = lambda: self.raise_bet(raise_amount)
        frame_game.after(100, chosen_action)

    # Method that chooses actions for the bot to take using hand information
    def smarter_bot_ai(self):
        # Weights for fold, check/call, raise
        action_weights = [0.15, 1, 0.2]
        # Variable for the maximum raise a player will make
        max_raise = pokerGame.max_bet
        # Changing weights of decisions and maximum raise based on hand rank
        # Straight flush hand
        if self.hand_rank == 9:
            action_weights[2] = 3
            action_weights[0] = 0
        # Hand better than a flush
        elif self.hand_rank > 6:
            action_weights[2] = 2
            action_weights[0] = 0
        # Hand better than three of a kind
        elif self.hand_rank > 4:
            action_weights[2] = 0.8
            action_weights[0] = 0.01
            max_raise = 50
        # Hand better than one pair
        elif self.hand_rank > 2:
            action_weights[2] = 0.6
            action_weights[0] = 0.05
            max_raise = 40
        # A high value high card hand
        elif int(self.best_hand[0][0:-1]) > 9:
            action_weights[0] = 0.1
            max_raise = 30
        # A normal high card hand
        else:
            max_raise = 20

        # If statement makes the bot unable to raise if their max bet does not meet the minimum raise
        if max_raise <= pokerGame.min_raise:
            action_weights[2] = 0

        # Prevents the player from raising if they have already raised
        if self.raised:
            action_weights[2] = 0

        # If the money needed to bet is greater than 100 double the chance of folding
        if (pokerGame.bet_to_match - self.current_bet) > 100:
            action_weights[0] = action_weights[0] * 2

        # Prevents players from raising more than they can
        if max_raise > self.money:
            max_raise = self.money

        # Creating a weighted list of actions
        weighted_list = random.choices(self.action_list, action_weights)
        # Randomly choosing an action from the weighted list
        chosen_action = random.choice(weighted_list)
        # Passes raise amount parameter if chosen action is to raise
        if chosen_action == self.raise_bet:
            raise_amount = random.randrange(pokerGame.min_raise, max_raise, 5)
            chosen_action = lambda: self.raise_bet(raise_amount)
        # After a certain amount of time call the chosen action
        frame_game.after(50, chosen_action)

    # Method to make the next player be able to act
    @classmethod
    def next_turn(cls):
        # Ends the game if there is only one player left
        if len(cls.active_player_list) == 1:
            cls.showdown()
            return
        # If the current player is at the end of the list then the next player is at the beginning
        if cls.current_turn.player_num == len(cls.player_list):
            cls.current_turn = cls.player_list[0]
        # Otherwise, the following player in the list is the next player
        else:
            # Finding the index of the current player and adding 1 to it
            player_location = cls.player_list.index(cls.current_turn)
            cls.current_turn = cls.player_list[player_location + 1]

        # Code to determine if every player has acted since the start of the round or the last raise.
        # A class attribute is used to determine this, this attribute is incremented after each player's turn.
        all_players_acted = False
        if cls.players_acted >= len(cls.player_list) - 1:
            all_players_acted = True

        # Only when all players have acted check if all bets are equal
        if all_players_acted:
            bets_equal = True
            # bets_equal will still be true at the end of this loop if all bets are equal
            for x in cls.active_player_list:
                if x.current_bet != cls.bet_to_match:
                    bets_equal = False
                    break
            # If all bets are equal then call next_round
            if bets_equal:
                # The starting player for next round is the person after the dealer.
                # So set the current player as the dealer.
                cls.current_turn = cls.dealer
                # -1 so all players can act in the next round
                cls.players_acted = -1
                cls.next_round()
                return

        # If the current player has folded then skip and move on to the next turn
        if cls.current_turn.fold_status:
            cls.players_acted += 1
            print(cls.players_acted)
            cls.next_turn()
            return

        # Changing the turn label to match the current player's turn
        label_turn.config(text="Player " + str(cls.current_turn.player_num) + "'s Turn")

        # Incrementing class attribute and allowing current player to act
        cls.players_acted += 1
        cls.player_action()

    # Method to increment round number and add community cards
    @classmethod
    def next_round(cls):
        # If it is the final round return
        if cls.round_num == 4 or len(cls.active_player_list) == 1:
            cls.showdown()
            return

        # Increments round counter
        cls.round_num = cls.round_num + 1
        # Updating round counter label
        label_round.config(text="Round " + str(cls.round_num))
        # If past the 2nd round deal 1 card per turn
        if cls.round_num > 2:
            cards_to_deal = 1
        # If it is the 2nd round deal 3 cards
        else:
            cards_to_deal = 3

        # Appends random cards to comCards
        for i in range(cards_to_deal):
            cls.com_cards.append(cls.gen_card())

        # Placeholders for community cards
        placeholders = [com_ph1, com_ph2, com_ph3, com_ph4, com_ph5]
        # Creating a range object to be used as a parameter in the displayCards method
        temp_range = range(len(cls.com_images), len(cls.com_images) + cards_to_deal)
        cls.display_cards(temp_range, cls.com_images, cls.com_cards, placeholders, (165, 240))

        # Resetting player's raised attribute
        for player in cls.active_player_list:
            player.raised = False
            player.hand_check()

        cls.next_turn()

    # Method used at the end of the game
    @classmethod
    def showdown(cls):
        # Changing label text and displaying the end game frame
        label_end.config(text="Game end")
        frame_interact.grid_forget()
        frame_end.grid(column=2, row=1, columnspan=2, sticky="NE")
        for player in cls.active_player_list:
            player.display_p_cards()

        # Calling win_check to determine the winner
        cls.win_check()
        # Giving the pot amount to the winner(s)
        if cls.draw:
            # Integer dividing the pot
            split_amount = cls.pot // len(cls.winner)
            # Gives each player their part of the pot
            for player in cls.winner:
                player.money = player.money + split_amount
        # If there is only one winner then give all money to them
        else:
            cls.winner[0].money = cls.winner[0].money + cls.pot

        for player in cls.active_player_list:
            hand_type = cls.hand_rank_dict[player.hand_rank]
            info_text = ("$" + str(player.money) + "\n" + hand_type)
            if player in cls.winner:
                info_text = ("Winner\n" + info_text)
            player.widgets[1].config(text=info_text)

        # Add 1 to the player's win number if they won
        if cls.player_list[0] in cls.winner:
            mycursor.execute("UPDATE users SET win_num = win_num + 1 WHERE ID = ?", (user_id,))
            # Saving changes
            conn.commit()
        # Add 1 to the player's bust number if they bust
        elif cls.player_list[0].money <= 0:
            mycursor.execute("UPDATE users SET bust_num = bust_num + 1 WHERE ID = ?", (user_id,))
            # Saving changes
            conn.commit()
            # Resetting player money
            cls.player_list[0].money = 1000

        # Update the player's money field and increment the games played field
        sql = "UPDATE users SET money = ?, games_played = games_played + 1 WHERE ID = ?"
        # Values to be used in the SQL code
        val = (cls.player_list[0].money, user_id)
        mycursor.execute(sql, val)
        # Saving changes
        conn.commit()

    # Method to reset some class attributes and to start a new game
    @classmethod
    def reset(cls):
        # Resetting class attributes
        cls.cards = [
            ["01S", "02S", "03S", "04S", "05S", "06S", "07S", "08S", "09S", "10S", "11S", "12S", "13S"],
            ["01H", "02H", "03H", "04H", "05H", "06H", "07H", "08H", "09H", "10H", "11H", "12H", "13H"],
            ["01C", "02C", "03C", "04C", "05C", "06C", "07C", "08C", "09C", "10C", "11C", "12C", "13C"],
            ["01D", "02D", "03D", "04D", "05D", "06D", "07D", "08D", "09D", "10D", "11D", "12D", "13D"]
        ]
        cls.com_cards = []
        cls.round_num = 1
        cls.winner = None
        cls.com_images = []
        cls.pot = 0
        cls.bet_to_match = cls.big_blind_amount
        cls.min_raise = cls.big_blind_amount
        cls.current_turn = None
        cls.starting_player = None
        cls.players_acted = 0

        # Hiding the end game frame and showing the game buttons
        frame_end.grid_forget()
        frame_interact.grid(column=3, row=1)
        # Resetting card images to card backs
        ph_list1 = [p1_ph1, p1_ph2]
        ph_list2 = [p2_ph1, p2_ph2, p3_ph1, p3_ph2, p4_ph1, p4_ph2, p5_ph1, p5_ph2]
        ph_list3 = [com_ph1, com_ph2, com_ph3, com_ph4, com_ph5]
        for x in ph_list1:
            x.config(image=back)
        for x in ph_list2:
            x.config(image=back_small)
        for x in ph_list3:
            x.config(image=blank_back)

        # Code to store money attribute for each player before deletion
        money_store = []
        for player in cls.player_list:
            # Code for if the player has ran out of money
            if player.money <= 0:
                player.money = 1000
            money_store.append(player.money)
            del player

        # Calling method to create the players again and give them their previous money attribute
        cls.create_players()

        for i in range(len(cls.player_list)):
            player = cls.player_list[i]
            player.money = money_store[i]

        # Configuring buttons to work with the new player object
        button_fold.config(command=pokerGame.player_list[0].fold)
        button_check_call.config(command=pokerGame.player_list[0].check_call)
        button_raise.config(command=lambda: pokerGame.player_list[0].raise_bet(slider_raise.get()))
        label_end.config(text="")

        # Calling method to continue the game
        cls.new_game()

    # Method to combine player cards and community cards
    def gen_p_and_com(self):
        # Combining player and community cards
        self.p_and_com = self.p_cards + pokerGame.com_cards

        # Sorting in descending order
        self.p_and_com.sort(reverse=True)

        # Creating an attribute that is a copy of pAndCom.
        # This attribute will include two versions of aces, 14 and 01, and be used for checking for ace high hands.
        self.p_and_com_ace = self.p_and_com.copy()
        # Creating list to see if pAndCom contains an ace
        temp_list = []
        # Removing the suits from the cards and appending them to temp_list
        for x in self.p_and_com:
            x = x[0:-1]
            temp_list.append(x)

        # If there is an ace, its location is found and used to find its suit
        for x in enumerate(temp_list):
            # Checking if the value of the element is "01"
            if x[1] == "01":
                # If it is then store the index of the element in a variable
                ace_location = (x[0])
                # 14 and the suit of the ace is then appended to pAndComAce
                self.p_and_com_ace.append('14' + (self.p_and_com_ace[ace_location])[-1])

        # Sorting this list in descending order
        self.p_and_com_ace.sort(reverse=True)

    # Function to check for matching cards.
    # i.e. one pair, two pairs, three of a kind, four of a kind.
    def match_check(self):

        # Creating list without ace low cards (01) as ace high cards (14) are present.
        # This is to prevent both ace cards from being detected as matches.
        p_and_com_temp = []
        for x in self.p_and_com_ace:
            if "01" not in x:
                p_and_com_temp.append(x)

        match_cards = []

        # Creating a loop that will run until it has gone through the player's hand.
        # While loop needs to be used because elements from list are removed.
        # i = -1 so it becomes 0 at the beginning of the loop.
        i = -1
        # Variable to hold number of types of matching cards
        num_of_matches = -1
        while i < (len(p_and_com_temp) - 1):
            i = i + 1
            # Variable to compare a card to the rest of the hand
            card_comp1 = p_and_com_temp[i]
            match_in_hand = False
            # Loop to compare card_comp1 to rest of cards in hand
            # While loop needs to be used because elements from list are removed
            card_comp2 = i
            while card_comp2 < (len(p_and_com_temp) - 1):
                card_comp2 = card_comp2 + 1
                # Checking if the cards values are the same by removing suit
                if card_comp1[:-1] == p_and_com_temp[card_comp2][:-1]:
                    if match_in_hand:
                        # Appending the matching card to the correct column in the 2d list
                        match_cards[num_of_matches].append(p_and_com_temp[card_comp2])
                        # Removing the matching card so it won't be selected again
                        p_and_com_temp.remove(p_and_com_temp[card_comp2])
                        # 1 is subtracted from card_comp2 to account for removing a card
                        card_comp2 = card_comp2 - 1
                    else:
                        match_in_hand = True
                        # Combining both cards into one list and are appended to paircard
                        match_cards.append([card_comp1, p_and_com_temp[card_comp2]])
                        # Removing the matching card so it won't be selected again
                        p_and_com_temp.remove(p_and_com_temp[card_comp2])
                        # 1 is subtracted from card_comp2 to account for removing a card
                        card_comp2 = card_comp2 - 1
                        num_of_matches = num_of_matches + 1

        # If there are any matches then set matches attribute to matching cards
        if len(match_cards) > 0:
            self.matches = match_cards
            self.matches.sort(reverse=True)
        else:
            # Otherwise make matches an empty list
            self.matches = []

    # Method to see if player has a straight
    def straight_check(self):
        # A straight is only possible with at least 5 cards, too early in game
        if len(self.p_and_com) < 5:
            # print("Straight not possible")
            return

        # Making a copy of pAndComAce attribute without duplicate values
        no_dup_list = self.p_and_com_ace.copy()
        # Using copy to create list without duplicates from pAndCom
        card_num1 = 0
        while card_num1 < len(no_dup_list):
            # + 1 so the same cards are not checked
            card_num2 = card_num1 + 1
            # While loop used instead of a for loop as list elements are removed
            while card_num2 < len(no_dup_list):
                # Checking if the value of each card is the same
                if no_dup_list[card_num1][0:-1] in no_dup_list[card_num2]:
                    # Removing if the value is the same
                    no_dup_list.pop(card_num2)
                # Incrementing card_num2
                card_num2 += 1
            # Incrementing card_num1
            card_num1 += 1

        # Creating a list without suits using the previously created list
        clean_list = []
        for x in no_dup_list:
            x = int(x[0:-1])
            clean_list.append(x)

        # print(no_dup_list)

        # This variable is used so only 5 cards are checked at a time
        upper_bound = 5

        # print("clean list = ", clean_list)
        # print(len(clean_list))

        # Range is the number of iterations needed to go through entire hand.
        # Checks 5 cards at a time.
        for i in range(len(clean_list) - 4):
            # print("i", i)
            # print("uB", upper_bound)

            # Temp list is the 5 cards that are checked per iteration
            tempList = clean_list[i:upper_bound]
            # print("temp list = ", tempList)
            # If the range of the temp list is equal to the length then the hand contains a straight
            if max(tempList) + 1 - min(tempList) == 5:
                # Straight attribute set to True
                print(no_dup_list[i:upper_bound])
                self.straight.append(no_dup_list[i:upper_bound])
            # Incrementing for next iteration
            upper_bound = upper_bound + 1

    # Method to see if player has a flush
    def flush_check(self):
        # A flush requires 5 cards
        if len(self.p_and_com) < 5:
            # print("Flush not possible")
            return

        # Function that returns only the suit, used as a key for the sort method
        def suit_key(x):
            return x[-1]

        p_and_com_temp = []
        # Code to remove 01 from the card list to prevent duplicate aces
        for x in self.p_and_com_ace:
            if "01" not in x:
                p_and_com_temp.append(x)

        p_and_com_temp.sort(reverse=True)
        # Sorting pAndCom list based on suit
        p_and_com_temp.sort(key=suit_key)
        # print("pAndCom", pAndCom)

        # p_and_com_temp = sorted(self.p_and_com_ace, key=suit_key)

        # Local variable used in checking if flush is present
        flush = False
        # Similar method to straightCheck.
        # Range is the number of iterations needed to go through entire hand.
        # Checks 5 cards at a time.
        for i in range(len(p_and_com_temp) - 4):
            # Local list to hold matching suit cards
            flush_cards = []
            # Suit of card to be compared to
            cardComp = p_and_com_temp[i][-1]
            flush_cards.append(p_and_com_temp[i])
            # Iterates through the 4 cards after cardComp
            for y in range(i + 1, i + 5):
                # Checks if the card suit matches cardComp
                if p_and_com_temp[y][-1] != cardComp:
                    flush = False
                    # Ends loop as flush is not possible with this set of cards
                    break
                else:
                    flush = True
                    # The matching card is appended to local list
                    flush_cards.append(p_and_com_temp[y])
            # If flush is still true meaning a flush is present the local flush list is appended to player attribute
            if flush:
                self.flush.append(flush_cards)
            # Flush variable reset for next series of checks
            flush = False
        # Sorting flush list in descending order
        self.flush.sort(reverse=True)

    # Method to see if player has a full house.
    # 3 cards of same value and 2 cards of another value.
    def full_house_check(self):
        # Utilises the matchCheck algorithm so call the matchCheck method if it has not been called yet
        if self.matches is None:
            self.match_check()
        # Full house only possible with 2 different card matches
        if len(self.matches) < 2:
            return
        # The matches list has been sorted in descending order.
        # So if the total number of cards in the first 2 columns of the matches list is equal to 5,
        # then the only possible combination is three matching cards and a pair so a full house is present
        elif len(self.matches[0]) + len(self.matches[1]) == 5:
            # Combining both in the full house attribute to create a single list
            self.full_house = self.matches[0].copy()
            self.full_house.extend(self.matches[1])

    # Method to check if player has a straight flush.
    # 5 cards of the same suit and sequential rank.
    def straight_flush_check(self):
        # Need to be a straight and flush in hand for straight flush to be possible
        if self.flush == [] or self.straight == []:
            return

        straight_flush = False
        # Checking if all cards in any of the possible straights are the same suit, i.e a flush
        for card_set in self.straight:
            straight_flush = True
            # Storing the suit to be compared to in a variable
            comp_card = card_set[0][-1]
            for card in card_set:
                # If the card suits are not the same then end the checks for this card set
                if card[-1] != comp_card:
                    straight_flush = False
                    break

        # If the straight is also a flush then it is a straight flush
        if straight_flush:
            self.straight_flush = self.straight[0]
            self.straight_flush.sort(reverse=True)

    # Method to determine a player's best hand
    def hand_check(self):
        # Calling all hand check methods
        self.gen_p_and_com()
        # self.pAndCom = ['04H', '04S', '02C', '03D', '13H', '09C', '06H']
        self.p_and_com.sort(reverse=True)
        self.match_check()
        self.match_type_check()
        self.straight_check()
        self.flush_check()
        self.full_house_check()
        self.straight_flush_check()
        # The loop ends when the best hand is found
        self.hand_rank = None
        while self.hand_rank is None:
            if self.straight_flush:
                self.hand_rank = 9
                self.best_hand = self.straight_flush
            elif self.match_type == "four of a kind":
                self.hand_rank = 8
                self.best_hand = self.match_hand
            elif self.full_house:
                self.hand_rank = 7
                self.best_hand = self.full_house
            elif self.flush:
                self.hand_rank = 6
                self.best_hand = self.flush[0]
            elif self.straight:
                self.hand_rank = 5
                self.best_hand = self.straight[0]
            elif self.match_type == "three of a kind":
                self.hand_rank = 4
                self.best_hand = self.match_hand
            elif self.match_type == "two pair":
                self.hand_rank = 3
                self.best_hand = self.match_hand
            elif self.match_type == "one pair":
                self.hand_rank = 2
                self.best_hand = self.match_hand
            else:
                self.hand_rank = 1
                # High card hand is the highest value cards in pAndCom
                p_and_com_temp = []
                for x in self.p_and_com_ace:
                    if "01" not in x:
                        p_and_com_temp.append(x)
                self.best_hand = p_and_com_temp[0:5]

    # Method to determine the type of match the player has.
    # e.g. one pair, two pair.
    def match_type_check(self):
        # If player has no matches return
        if not self.matches:
            return
        # Number of cards in first column, which is the largest column
        # As self.matches has been sorted in descending order
        first_match_length = len(self.matches[0])

        # Creating a copy of pAndCom without cards from the matches list
        # This will be used for kickers, separate cards from the matching cards
        temp_list = []
        for x in self.p_and_com_ace:
            # Removing all '01' ace versions as '14' ace versions are already present
            if "01" in x:
                continue
            # Loop will go through each column of matches
            for b in range(len(self.matches)):
                # If the card is present in matches ignore it and move on
                if x in self.matches[b]:
                    break
                # If the card is not present then append to the list
                else:
                    temp_list.append(x)
        # Sorting in descending order
        temp_list.sort(reverse=True)

        # Making matchHand equal to the first column of matches
        self.match_hand = self.matches[0].copy()

        # If the first column contains 4 cards it is a four of a kind
        if first_match_length == 4:
            self.match_type = "four of a kind"
            # Appending card to the hand to act as the kicker
            self.match_hand.append(temp_list[0])
        # If the first column contains 3 cards it is a three of a kind
        elif first_match_length == 3:
            self.match_type = "three of a kind"
            # Appending 2 cards to the hand to act as the kicker
            self.match_hand.extend(temp_list[0:2])
        # At this point match must be a two or one pair
        # If there is more than 1 column it must be two pair
        elif len(self.matches) > 1:
            self.match_type = "two pair"
            # Appending second pair to matchHand
            self.match_hand.extend(self.matches[1])
            # Appending kicker
            self.match_hand.append(temp_list[0])
        # Otherwise, if there is only one column it is one pair
        else:
            self.match_type = "one pair"
            # Appending 3 kickers
            self.match_hand.extend(temp_list[0:3])

    # Method to determine winner by seeing who has the better hand
    @classmethod
    def win_check(cls):
        # If there is only one player left then make them the winner
        global draw
        if len(cls.active_player_list) == 1:
            cls.winner = [cls.active_player_list[0]]
            return
        # Temporary variable to hold winner
        winner_temp = None
        # List for players that draw
        draw_list = []
        # First player is assigned to player_comp for comparisons
        player_comp = cls.active_player_list[0]

        for i in range(1, len(cls.active_player_list)):
            # Player to be compared to player_comp is assigned to player_comp2
            player_comp2 = cls.active_player_list[i]
            # Both players are compared to determine who has a better hand
            if player_comp.hand_rank > player_comp2.hand_rank:
                winner_temp = player_comp
            elif player_comp2.hand_rank > player_comp.hand_rank:
                winner_temp = player_comp2
                # Player_comp is changed to the winning player to be compared in the next iteration
                player_comp = player_comp2

            # If they have the same hand type then compare the value of cards in the hand
            else:
                for a in range(len(player_comp.best_hand)):
                    draw = True
                    # Comparing each card in each hand
                    if player_comp.best_hand[a][0:-1] > player_comp2.best_hand[a][0:-1]:
                        winner_temp = player_comp
                        draw = False
                        break
                    elif player_comp2.best_hand[a][0:-1] > player_comp.best_hand[a][0:-1]:
                        winner_temp = player_comp2
                        # Player_comp is changed to the winning player to be compared in the next iteration
                        player_comp = player_comp2
                        draw = False
                        break
                # If statement for if the player's hands have the same value
                if draw:
                    # Hands are equal in value but set winner_temp to player_comp2 for future checks
                    winner_temp = player_comp2
                    # If this is the first draw then append player_comp
                    if len(draw_list) == 0:
                        draw_list.append(player_comp)
                    # Appending player_comp2
                    draw_list.append(player_comp2)
                    break

        # If winner_temp is in draw_list then two or more players have the same best hands
        if winner_temp in draw_list:

            cls.draw = True
            # Making the class attribute winner equal to the draw_list
            cls.winner = draw_list
        else:
            # Assigning winner to class attribute
            cls.winner = [winner_temp]


# def random_ai():
#     decision_list = ("FOLD", "CHECK", "RAISE")
#     decision = random.choice(decision_list)
#     print(decision)
#     activity_2.config(text="Player 2 = "+decision)


# GUI

root = tk.Tk()  # creating window named root
root.title("Poker")  # changing window title


# Changing size of window
# root.geometry("1205x720")

# Function to hide menu frame and show game frame
def resume():
    # Hiding the menu frame
    frame_menu.grid_forget()
    frame_game.grid()
    return


# Function to hide game frame and show menu frame
def hide_game():
    frame_game.grid_forget()
    frame_menu.grid()


# Checks if given details are in the database
def login():
    # Retrieving all username and password combinations from the users table
    mycursor.execute("SELECT username, password FROM users")
    myresult = mycursor.fetchall()
    # Getting the user inputs for username and password
    inp_username = entry_user.get()
    inp_password = entry_pass.get()
    # Checking if the given username and password is blank
    if inp_username == "" or inp_password == "":
        print("Enter a username and password")
        label_explain1.config(text="Enter a username and password")
        return
    # Checking if the given username and password combination is in the users table
    elif (inp_username, inp_password) in myresult:
        # Retrieving the user's ID and money attribute
        mycursor.execute("SELECT ID, money FROM users WHERE username = ?", (inp_username,))
        # Storing this data in variables
        global user_id
        player_data = mycursor.fetchone()
        user_id = player_data[0]
        global user_money
        user_money = player_data[1]
        # Disabling the login button
        button_login.config(state="disabled")
        # Hiding the login frame
        frame_login.grid_forget()
        # Showing the menu frame
        frame_menu.grid(column=0, row=0)

        label_welcome.config(text="Welcome " + inp_username)
        label_menu_money.config(text="Money = $" + str(user_money))
    # No matching username and password combination
    else:
        print("Incorrect username or password")
        label_explain1.config(text="Incorrect username or password")


# Function used to create to show frame for registering
def register():
    frame_login.grid_forget()
    frame_reg.grid(column=0, row=0)


# Function to hide the register frame
def hide_reg():
    frame_reg.grid_forget()
    frame_login.grid()


# Storing given username and password in a database
def create_account():
    mycursor.execute("SELECT username FROM users")
    print(mycursor)
    myresult = mycursor.fetchall()
    print(myresult)
    new_user = entry_new_user.get()
    new_pass = entry_new_pass.get()
    if len(new_user) < 4:
        label_explain2.config(text="Username has to be at least 4 characters")
        return
    elif (new_user,) in myresult:
        label_explain2.config(text="Username is already taken")
        return
    elif len(new_pass) < 4:
        label_explain2.config(text="Password has to be at least 4 characters")
        return
    elif len(new_user) > 16 or len(new_pass) > 16:
        label_explain2.config(text="Username and password cannot be longer than 16 characters")
        return
    else:
        sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        val = (new_user, new_pass)
        mycursor.execute(sql, val)
        conn.commit()
        button_enter.config(text="Registered!", state="disabled")


# Method to show player statistics
def show_stats():
    # Hiding menu frame
    frame_menu.grid_forget()
    # Retrieve player information using their ID
    mycursor.execute("SELECT username, win_num, bust_num, games_played FROM users WHERE ID = ?", (user_id,))
    myresult = mycursor.fetchone()
    # Configuring labels to show their information
    label_username.config(text="Username = " + str(myresult[0]))
    label_wins.config(text="Wins = " + str(myresult[1]))
    label_busts.config(text="Busts = " + str(myresult[2]))
    label_games_played.config(text="Games played = " + str(myresult[3]))
    frame_stats.grid(column=0, row=0, padx=10, pady=10)


# Method to hide the stats frame and show the menu frame
def hide_stats():
    frame_stats.grid_forget()
    frame_menu.grid(column=0, row=0)


def open_info():

    def show_htp_tab():
        hr_frame.grid_forget()
        htp_frame.grid(column=1, row=0, rowspan=2)
        hr_button.config(state="active")
        htp_button.config(state="disabled")

    def show_hr_tab():
        htp_frame.grid_forget()
        hr_frame.grid(column=1, row=0, rowspan=2)
        htp_button.config(state="active")
        hr_button.config(state="disabled")

    info_window = tk.Toplevel(root)
    hr_button = tk.Button(info_window, text="Hand ranks", width=10, height=8, command=show_hr_tab, state="disabled",
                          font="Roboto 16")
    hr_button.grid(column=0, row=0)
    htp_button = tk.Button(info_window, text="How to play", width=10, height=8, command=show_htp_tab, font="Roboto 16")
    htp_button.grid(column=0, row=1)

    hr_frame = tk.Frame(info_window)
    hr_frame.grid(column=1, row=0, rowspan=2)
    hr_title = tk.Label(hr_frame, text="Hand ranks (highest to lowest)", font="Roboto 18")
    hr_title.grid(column=0, row=0)

    hr_text = read_file("handranks.txt")
    hr_label = tk.Label(hr_frame, text=hr_text, font="Roboto 16")
    hr_label.grid(column=0, row=1)

    htp_frame = tk.Frame(info_window)
    htp_frame.grid(column=1, row=0, rowspan=2)
    htp_frame.grid_forget()

    htp_text = read_file("howtoplay.txt")
    htp_label = tk.Label(htp_frame, text=htp_text, font="Roboto 14")
    htp_label.grid(column=0, row=0, rowspan=2)


def read_file(file):
    text_file = open(file, "r")
    data = text_file.read()
    text_file.close()
    return data


############################################################################################

# Frame for the login screen
# A frame acts as a container for widgets
frame_login = tk.Frame(root)
frame_login.grid(column=0, row=0)

# Creating widgets for the login frame
label_login = tk.Label(frame_login, text="Login", font="Roboto 24",)
label_username_inp = tk.Label(frame_login, text="Username:", font="Roboto 16")
label_password_inp = tk.Label(frame_login, text="Password:", font="Roboto 16")
label_explain1 = tk.Label(frame_login, text="", font="Roboto 16", wraplength=200)
entry_user = tk.Entry(frame_login, font="Roboto 16")
entry_pass = tk.Entry(frame_login, font="Roboto 16")

button_login = tk.Button(frame_login, text="Login", font="Roboto 16", width=20, height=3, command=login)
button_register = tk.Button(frame_login, text="Register an account", font="Roboto 16", width=16, height=3, command=register)

# Placing widgets in the login frame
label_login.grid(column=0, row=0)
label_username_inp.grid(column=0, row=1)
label_password_inp.grid(column=0, row=2)
label_explain1.grid(column=1, row=0)
entry_user.grid(column=1, row=1, ipady=5)
entry_pass.grid(column=1, row=2, ipady=5)

button_login.grid(column=1, row=3)
button_register.grid(column=0, row=3)

# Creating frame for registering

frame_reg = tk.Frame(root)

label_explain2 = tk.Label(frame_reg, text="Enter a new username and password", font="Roboto 16", wraplength=600)
label_user = tk.Label(frame_reg, text="Username:", font="Roboto 16")
label_pass = tk.Label(frame_reg, text="Password:", font="Roboto 16")
entry_new_user = tk.Entry(frame_reg, font="Roboto 16")
entry_new_pass = tk.Entry(frame_reg, font="Roboto 16")
button_enter = tk.Button(frame_reg, text="Enter", font="Roboto 16", width=20, height=3, command=create_account)
button_close = tk.Button(frame_reg, text="Close", font="Roboto 16", width=16, height=3, command=hide_reg)

# placing widgets
label_explain2.grid(column=0, row=0, columnspan=2)
label_user.grid(column=0, row=1)
label_pass.grid(column=0, row=2)
entry_new_user.grid(column=1, row=1, ipady=5)
entry_new_pass.grid(column=1, row=2, ipady=5)
button_enter.grid(column=1, row=3)
button_close.grid(column=0, row=3)

# Menu frame
frame_menu = tk.Frame(root)

# Menu widgets
label_welcome = tk.Label(frame_menu, text="Welcome", font="Roboto 16")
label_menu_money = tk.Label(frame_menu, text="Your money : ", font="Roboto 16")
button_play = tk.Button(frame_menu, text="Play", font="Roboto 16", width=20, height=3, command=pokerGame.start)
button_stats = tk.Button(frame_menu, text="Your Stats", font="Roboto 16", width=20, height=3, command=show_stats)
button_exit = tk.Button(frame_menu, text="Exit", font="Roboto 16", width=20, height=3, command=root.destroy)
label_welcome.grid(column=0, row=0)
label_menu_money.grid(column=0, row=1)
button_play.grid(column=0, row=2)
button_stats.grid(column=0, row=3)
button_exit.grid(column=0, row=4)

# Frame for statistics

frame_stats = tk.Frame(root)

label_username = tk.Label(frame_stats, text="Username = ", font="Roboto 16")
label_wins = tk.Label(frame_stats, text="Times won = ", font="Roboto 16")
label_busts = tk.Label(frame_stats, text="Times bust = ", font="Roboto 16")
label_games_played = tk.Label(frame_stats, text="Games played = ", font="Roboto 16")
button_back = tk.Button(frame_stats, text="Back", font="Roboto 16", command=hide_stats)

label_username.grid(column=0, row=0)
label_wins.grid(column=0, row=1)
label_busts.grid(column=0, row=2)
label_games_played.grid(column=0, row=3)
button_back.grid(column=0, row=4)

###############################
# creating frame for the game #
###############################
frame_game = tk.Frame(root)
frame_game.grid(column=0, row=0)
frame_game.grid_forget()

temp_img = Image.open("card_png/abstract_clouds.png")
back = temp_img.resize((165, 240))
back_small = temp_img.resize((84, 120))
back = ImageTk.PhotoImage(back)
back_small = ImageTk.PhotoImage(back_small)

temp_img2 = Image.open("card_png/blank_card.png")
blank_back = temp_img2.resize((165, 240))
blank_back_small = temp_img2.resize((84, 120))
blank_back = ImageTk.PhotoImage(blank_back)
blank_back_small = ImageTk.PhotoImage(blank_back_small)

# label_3 = tk.Label(frame_game, text="GAME")
# canvas = tk.Canvas(frame_game, width=800, height=300)


###################################
# creating frame for player 1 cards #
###################################
frame_p1 = tk.Frame(frame_game)
frame_p1.grid(column=1, row=1, sticky="W")

label_p1 = tk.Label(frame_p1, text="Player 1", font="Roboto 16")
label_p1_act = tk.Label(frame_p1, text="", font="Roboto 16")
p1_ph1 = tk.Label(frame_p1, image=back)
p1_ph2 = tk.Label(frame_p1, image=back)
label_p1_info = tk.Label(frame_p1, text="$", font="Roboto 16")

label_p1.grid(column=0, row=0)
label_p1_act.grid(column=1, row=0)
p1_ph1.grid(column=0, row=1, padx="5", pady="5")
p1_ph2.grid(column=1, row=1, padx="5", pady="5")
label_p1_info.grid(column=2, row=1)

#####################################
# creating frame for other players
#####################################
frame_op = tk.Frame(frame_game)
frame_op.grid(column=0, row=0, sticky="NW", rowspan=2)

label_p2 = tk.Label(frame_op, text="Player 2", font="Roboto 16")
label_p2_act = tk.Label(frame_op, font="Roboto 16")
p2_ph1 = tk.Label(frame_op, image=back_small)
p2_ph2 = tk.Label(frame_op, image=back_small)
label_p2_info = tk.Label(frame_op, text="$", font="Roboto 16")
label_hand_type2 = tk.Label(frame_op, text="P2 Hand type = Nothing", font="Roboto 16")

label_p2.grid(column=0, row=0)
label_p2_act.grid(column=1, row=0)
p2_ph1.grid(column=0, row=1, padx="5", pady="5")
p2_ph2.grid(column=1, row=1, padx="5", pady="5")
label_p2_info.grid(column=2, row=1)
# label_hand_type2.grid(column=2, row=2)

label_p3 = tk.Label(frame_op, text="Player 3", font="Roboto 16")
label_p3_act = tk.Label(frame_op, font="Roboto 16")
p3_ph1 = tk.Label(frame_op, image=back_small)
p3_ph2 = tk.Label(frame_op, image=back_small)
label_p3_info = tk.Label(frame_op, text="$", font="Roboto 16")
label_hand_type3 = tk.Label(frame_op, text="P3 Hand type = Nothing", font="Roboto 16")

label_p3.grid(column=0, row=2)
label_p3_act.grid(column=1, row=2)
p3_ph1.grid(column=0, row=3, padx="5", pady="5")
p3_ph2.grid(column=1, row=3, padx="5", pady="5")
label_p3_info.grid(column=2, row=3)
# label_hand_type3.grid(column=2, row=4)

label_p4 = tk.Label(frame_op, text="Player 4", font="Roboto 16")
label_p4_act = tk.Label(frame_op, font="Roboto 16")
p4_ph1 = tk.Label(frame_op, image=back_small)
p4_ph2 = tk.Label(frame_op, image=back_small)
label_p4_info = tk.Label(frame_op, text="$", font="Roboto 16")
label_hand_type4 = tk.Label(frame_op, text="P4 Hand type = Nothing", font="Roboto 16")

label_p4.grid(column=0, row=4)
label_p4_act.grid(column=1, row=4)
p4_ph1.grid(column=0, row=5, padx="5", pady="5")
p4_ph2.grid(column=1, row=5, padx="5", pady="5")
label_p4_info.grid(column=2, row=5)
# label_hand_type4.grid(column=2, row=6)

label_p5 = tk.Label(frame_op, text="Player 5", font="Roboto 16")
label_p5_act = tk.Label(frame_op, font="Roboto 16")
p5_ph1 = tk.Label(frame_op, image=back_small)
p5_ph2 = tk.Label(frame_op, image=back_small)
label_p5_info = tk.Label(frame_op, text="$", font="Roboto 16")
label_hand_type5 = tk.Label(frame_op, text="P5 Hand type = Nothing", font="Roboto 16")

label_p5.grid(column=0, row=6)
label_p5_act.grid(column=1, row=6)
p5_ph1.grid(column=0, row=7, padx="5", pady="5")
p5_ph2.grid(column=1, row=7, padx="5", pady="5")
label_p5_info.grid(column=2, row=7)
# label_hand_type5.grid(column=2, row=8)


######################################
# creating frame for community cards #
######################################
frame_c = tk.Frame(frame_game)
frame_c.grid(column=1, row=0, sticky="NW", columnspan=3)

label_c = tk.Label(frame_c, text="Community cards", font="Roboto 16")
com_ph1 = tk.Label(frame_c, image=blank_back)
com_ph2 = tk.Label(frame_c, image=blank_back)
com_ph3 = tk.Label(frame_c, image=blank_back)
com_ph4 = tk.Label(frame_c, image=blank_back)
com_ph5 = tk.Label(frame_c, image=blank_back)

label_c.grid(column=0, row=0)
com_ph1.grid(column=0, row=1, padx="5", pady="5")
com_ph2.grid(column=1, row=1, padx="5", pady="5")
com_ph3.grid(column=2, row=1, padx="5", pady="5")
com_ph4.grid(column=3, row=1, padx="5", pady="5")
com_ph5.grid(column=4, row=1, padx="5", pady="5")

##################################
# creating frame for interaction #
##################################
frame_interact = tk.Frame(frame_game, padx=5, pady=5)
frame_interact.grid(column=2, row=1, columnspan=2, sticky="NE")

button_menu = tk.Button(frame_interact, text="Menu", font="Roboto 16", width=10, height=1, command=hide_game)
button_info = tk.Button(frame_interact, text="Info", font="Roboto 16", width=10, height=1, command=open_info)
# buttons are disabled until start button pressed
button_fold = tk.Button(frame_interact, text="Fold", font="Roboto 16", width=10, height=4, state="disabled")
button_check_call = tk.Button(frame_interact, text="Check", font="Roboto 16", width=10, height=4, state="disabled")
button_raise = tk.Button(frame_interact, text="Raise", font="Roboto 16", width=10, height=4, state="disabled")

label_raise_amount = tk.Label(frame_interact, text="Raise amount", font="Roboto 12")
slider_raise = tk.Scale(frame_interact, to=0, from_=50, width=20)

button_menu.grid(column=1, row=0, sticky="W")  # showing the menu frame
button_info.grid(column=1, row=1)
# tk.Label(frame_interact, text=" ").grid(column=0, row=2)
button_fold.grid(column=1, row=3)
button_check_call.grid(column=1, row=4)
button_raise.grid(column=1, row=5)
label_raise_amount.grid(column=0, row=4, sticky="S", padx=5)
slider_raise.grid(column=0, row=5)

# creating frame for general info

frame_info = tk.Frame(frame_game)
frame_info.grid(column=2, row=1, sticky="N", pady=5)

label_pot = tk.Label(frame_info, text="Pot = $0", font="Roboto 18")
label_round = tk.Label(frame_info, text="Round", font="Roboto 18")
label_turn = tk.Label(frame_info, text="No one's turn", font="Roboto 18")
label_end = tk.Label(frame_info, text="", font="Roboto 18")

label_pot.grid(column=0, row=0)
label_round.grid(column=0, row=1)
label_turn.grid(column=0, row=2)
label_end.grid(column=0, row=10)

# Creating frame for end game
frame_end = tk.Frame(frame_game)

button_new_game = tk.Button(frame_end, text="New Game", font="Roboto 16", width=10, height=3, command=pokerGame.reset)
button_new_game.grid(column=0, row=0)

# ends loop to allow buttons to function
root.mainloop()
