from domain import *

def user(): return User("USER1", "FB_ID", "User", "One", "user.jpg")
def player(): return Player("player_id", "owner_user_id", True, "image_url", "first_name", "last_name", "RIGHT", "notes", "phone_number", "email", 5.0)
def match(): return Match("match_id", "user_id", datetime(2020, 1, 1), "team1_player1_id", "team1_player2_id", "team2_player1_id", "team2_player2_id", "scores")
