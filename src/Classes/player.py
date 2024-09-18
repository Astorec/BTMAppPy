from datetime import datetime

# This is used to store the info that we gather from the Participants from the Challonge API
# and is also combined with the data that we store on Google Sheets
class Player:
    __name = ""
    __email = ""
    __checkInState = False
    __checkInTime = datetime.min
    __challongeId = ""
    __group_id = 0
    __leaderBoardRank = "n/a"
    __points = 0
    __wins = 0
    __loses = 0
    __first = 0
    __second = 0
    __third = 0
    __winPercentage = 0
    __raiting = 0
    __region = ""
    
    def __init__(self, name, challongeId, group_id):
        self.__name = name
        self.__challongeId = challongeId
        self.__group_id = group_id
    
    def updateScore(self, wins, losses):
        self.__wins += wins
        self.__loses += losses
        
    def addFirst(self):
        self.__first += 1
    
    def addSecond(self):
        self.__second += 1
    
    def addThird(self):
        self.__third += 1
        
    def get_id(self):
        return self.__challongeId
    
    def get_group_id(self):
        return self.__group_id
    
    def get_name(self):
        return self.__name
    
    def get_rank(self):
        return self.__leaderBoardRank
    
    def get_wins(self):
        return self.__wins
    
    def get_losses(self):
        return self.__loses
    
    def get_first(self):
        return self.__first
    
    def get_second(self):
        return self.__second
    
    def get_third(self):
        return self.__third
    
    def get_points(self):
        return self.__points
    
    def get_win_percentage(self):
        return self.__winPercentage
    
    def get_raiting(self):
        return self.__raiting
    
    def get_region(self):
        return self.__region
    
    def set_rank(self, rank):
        self.__leaderBoardRank = rank
        