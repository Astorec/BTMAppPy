class Match:
    __id = 0
    __identifier = ""
    __group_id = ""
    __loserId = 0
    __winnerId = 0
    __player1Score = 0
    __player2Score = 0
    __player1Id = 0
    __player2Id = 0
    __scores_csv = ""
    __state = ""
    __tournamentId = 0
    
    def __init__ (self, id, player1Id, player2Id, identifier, group_id, player1PrereqMatchId, player2PrereqMatchId, round, state, tournamentId, scores_csv):
        self.__id = id
        self.__scores_csv = scores_csv
        self.__player1Id = player1Id
        self.__player2Id = player2Id
        self.__identifier = identifier
        self.__group_id = group_id
        self.__state = state
        self.__tournamentId = tournamentId
    
    def get_id(self):
        return self.__id
    
    def get_player1_id(self):
        return self.__player1Id
    
    def get_player2_id(self):
        return self.__player2Id
    
    def get_identifier(self):
        return self.__identifier
    
    def get_group_id(self):
        return self.__group_id
    
    def get_winner_id(self):
        return self.__winnerId
    
    def get_loser_id(self):
        return self.__loserId
    def get_scores(self):
        return self.__scores_csv
    
    def get_state(self):
        return self.__state
    
