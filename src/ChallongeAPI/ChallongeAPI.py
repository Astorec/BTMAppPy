import challonge
from Classes.match import Match
from Classes.player import Player
from Classes.tournament import Tournament
from Classes.participant import Participant

class ChallongeAPI:
    def __init__(self, username, api_key):
        challonge.set_credentials(username, api_key)
        
    def create_tournament(name, desc, t_type):
        params = {
            "description": desc         
        }
        
        
        # remove spaces from name to create the url
        url = name.replace(" ", "")
        
        t = challonge.tournaments.create(name, url, str(t_type).lower(), **params)
        
        return Tournament(t['url'], t['id'], t['name'], t['started_at'], t['created_at'])
        
       
    def get_tournament(self, url):        
        t =  challonge.tournaments.show(url)
        return Tournament(t['url'], t['id'], t['name'], t['state'], t['participants_count'], t['started_at'], t['created_at'])
    

    
    def get_matches(self, tournament_id):
        m = challonge.matches.index(tournament_id)
        l = []
        
        for match in m:
            l.append(Match(match['id'], match['player1_id'], match['player2_id'], match['identifier'], match['group_id'],
                           match['player1_prereq_match_id'], match['player2_prereq_match_id'], 
                           match['round'], match['state'], match['tournament_id'], match['scores_csv']))
        return l
    
    def set_match_scores(self, tournament_id, match_id, scores_csv, winner_id, loser_id):
        params = {
            "scores_csv": scores_csv,
            "winner_id": winner_id,
            "loser_id": loser_id,
            "state": "complete"
        }
        challonge.matches.update(tournament_id, match_id, **params)
    
    def undo_match(self, tournament_id, match_id):
        challonge.matches.reopen(tournament_id, match_id)
    def get_participants(self, tournament_id):
        p = challonge.participants.index(tournament_id)
        l = []
        for participant in p:
            l.append(Participant(participant['checked_in_at'], participant['group_id'], participant['group_player_ids'],
                                 participant['id'], participant['name'], participant['tournament_id'], 
                                 participant['challonge_username'], participant['username'], participant['checked_in']))
        return l
    
    def add_participant(tournament_id, name):
        p = challonge.participants.create(tournament_id, name)
    
    def start_tournament(self, tournament_id):
        challonge.tournaments.start(tournament_id)  
        
    
    
    