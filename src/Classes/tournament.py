from enum import Enum

class Tournament:
    __url = ""
    __id = 0
    __name = ""
    __relatedSheet = ""
    _startAt = None
    _createdAt = None
    __isCompleted = False
    __addedToMainSheet = False
    __group_stages_enabled = False
    __tournament_type = "single elimination"
    __swiss_rounds = 0
    __category = "Beyblade X"
    
    def __init__(self, url, id, name, startedAt = None, createdAt = None, tournament_type = "single elimination", swiss_rounds = 0):
        self.__url = url
        self.__id = id
        self.__name = name
        self._startAt = startedAt
        self._createdAt = createdAt
        self.__tournament_type = tournament_type
        self.__swiss_rounds = swiss_rounds
        
        if startedAt is not None:
            self.__relatedSheet = "{} - {}".format(name, startedAt.strftime("%d/%m/%Y"))
        else:
            self.__relatedSheet = "{}-{}".format(name, createdAt)
        
    def get_url(self):
        return self.__url
    
    def get_name(self):
        return self.__name
    
    def get_id(self):
        return self.__id   
    
    def get_related_sheet(self):
        return self.__relatedSheet
    
    def get_tournament(self):
        return self