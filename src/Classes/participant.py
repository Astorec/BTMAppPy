from datetime import datetime
class Participant:
    __checked_in_at = datetime.min
    __group_id = 0
    __group_player_ids = []
    __id = 0
    __name = ""
    __tournament_id = 0
    __challonge_username = None
    __username = None
    __checked_in = False
    
    def __init__(self, checked_in_at, group_id, group_player_ids, id, name, tournament_id, challonge_username, username, checked_in):
        self.__checked_in_at = checked_in_at
        self.__group_id = group_id
        self.__group_player_ids = group_player_ids
        self.__id = id
        self.__name = name
        self.__tournament_id = tournament_id
        self.__challonge_username = challonge_username
        self.__username = username
        self.__checked_in = checked_in
        
    def get_name(self):
        return self.__name
    def get_checked_in_at(self):
        return self.__checked_in_at
    def get_id(self):
        return self.__id
    def get_group_id(self):
        return self.__group_id
    def get_group_player_ids(self):
        return self.__group_player_ids
    def get_checked_in(self):
        return self.__checked_in