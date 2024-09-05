class Match:
    __id = 0
    __identifier = ""
    __loserId = 0
    __winnerId = 0
    __player1Id = 0
    __player2Id = 0
    __state = ""
    __tournamentId = 0
    
    def __init__ (self, id, player1Id, player2Id, player1PrereqMatchId, player2PrereqMatchId, round, state, tournamentId):
        self.__id = id
        self.__player1Id = player1Id
        self.__player2Id = player2Id
        self.__state = state
        self.__tournamentId = tournamentId
    
    def get_id(self):
        return self.__id
    
    def get_player1_id(self):
        return self.__player1Id
    
    def get_player2_id(self):
        return self.__player2Id
    
    def get_winner_id(self):
        return self.__winnerId
    
    def get_loser_id(self):
        return self.__loserId