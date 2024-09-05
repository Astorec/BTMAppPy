import challonge
from Classes.match import Match
from Classes.player import Player
from Classes.tournament import Tournament
from Classes.participant import Participant

class ChallongeAPI:
    def __init__(self, username, api_key):
        challonge.set_credentials(username, api_key)
       
    def get_tournament(self, url):        
        t =  challonge.tournaments.show(url)
        return Tournament(t['url'], t['id'], t['name'], t['started_at'], t['created_at'])
    
    def get_matches(self, tournament_id):
        m = challonge.matches.index(tournament_id)
        l = []
        
        for match in m:
            l.append(Match(match['id'], match['player1_id'], match['player2_id'], 
                           match['player1_prereq_match_id'], match['player2_prereq_match_id'], 
                           match['round'], match['state'], match['tournament_id']))
        return l
    
    def get_participants(self, tournament_id):
        p = challonge.participants.index(tournament_id)
        l = []
        for participant in p:
            l.append(Participant(participant['checked_in_at'], participant['group_id'], participant['group_player_ids'],
                                 participant['id'], participant['name'], participant['tournament_id'], 
                                 participant['challonge_username'], participant['username'], participant['checked_in']))
        return l
        
    
    