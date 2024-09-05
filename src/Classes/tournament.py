class Tournament:
    __url = ""
    __id = 0
    __name = ""
    __relatedSheet = ""
    _startAt = None
    _createdAt = None
    __isCompleted = False
    __addedToMainSheet = False
    
    def __init__(self, url, id, name, startedAt = None, createdAt = None):
        self.__url = url
        self.__id = id
        self.__name = name
        self._startAt = startedAt
        self._createdAt = createdAt
        
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
    