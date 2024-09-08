import configparser

class GetConfig():
    #region Create Config
    def create_config():
        config = configparser.ConfigParser()

        config['CHALLONGE'] = { 'USERNAME': '',
                                'API_KEY': '' }
        
        config['GOOGLE_SHEETS'] = { 'URL': '' }

        config['TOURNAMENT_DETAILS'] = {'URL': '', 'Previous Tournaments': '[]'}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    #endregion
            
    #region Read Config
    def read_config():
        config = configparser.ConfigParser()

        # Check if the config file exists if not we create a new one with default values
        if not config.read('config.ini'):
            GetConfig.create_config()
            
        config.read('config.ini')
        return config
    #endregion

    def write_config(config):
        # Check to see if the current url exists in the previous tournaments list
        # If it does not exist we add it to the list
        if config['TOURNAMENT_DETAILS']['URL'] not in config['TOURNAMENT_DETAILS']['Previous Tournaments']:
            previous_tournaments = eval(config['TOURNAMENT_DETAILS']['Previous Tournaments'])
            previous_tournaments.append(config['TOURNAMENT_DETAILS']['URL'])
            config['TOURNAMENT_DETAILS']['Previous Tournaments'] = str(previous_tournaments)
            
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    
    #region Getters    
    def get_challonge_username():
        config = GetConfig.read_config()
        return config['CHALLONGE']['USERNAME']
    
    def get_challonge_api_key():
        config = GetConfig.read_config()
        return config['CHALLONGE']['API_KEY']
    
    def get_google_sheets_url():
        config = GetConfig.read_config()
        return config['GOOGLE_SHEETS']['URL']
    
    def get_previous():
        config = GetConfig.read_config()
        return eval(config['TOURNAMENT_DETAILS']['Previous Tournaments'])
    
    def set_url(url):
        config = GetConfig.read_config()
        config['TOURNAMENT_DETAILS']['URL'] = url
        GetConfig.write_config(config)
    #endregion
    