import challonge
from Classes.match import Match
from Classes.player import Player
from Classes.tournament import Tournament
from Classes.participant import Participant
import asyncio

class ChallongeAPI:
    def __init__(self, username, api_key):
        challonge.set_credentials(username, api_key)
        
    async def create_tournament(name, desc, t_type):
        params = {
            "description": desc  
        }
        
        # Extract tournament type from t_type
        if t_type == "Round Robin (16 or Less players)":
            t_type = "round robin"

        # remove spaces from name to create the url
        url = name.replace(" ", "")
        
        t = await challonge.tournaments.create(name, url, str(t_type).lower(), **params)
        
        
        return Tournament(t['url'], t['id'], t['name'], t['started_at'], t['created_at'])
        
       
    async def get_tournament(self, url):        
        t = await asyncio.to_thread(challonge.tournaments.show, url)
        return Tournament(t['url'], t['id'], t['name'], t['state'], t['participants_count'], t['started_at'], t['created_at'], t['tournament_type'])
    

    
    async def get_matches(self, tournament_id):
        m = await asyncio.to_thread(challonge.matches.index, tournament_id)
        l = []
        
        for match in m:
            l.append(Match(match['id'], match['player1_id'], match['player2_id'], match['identifier'], match['group_id'],
                           match['player1_prereq_match_id'], match['player2_prereq_match_id'], 
                           match['round'], match['state'], match['tournament_id'], match['scores_csv'], match['winner_id'], 
                           match['loser_id']))
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
    async def get_participants(self, tournament_id):
        p = await asyncio.to_thread(challonge.participants.index, tournament_id)
        l = []
        for participant in p:
            l.append(Participant(participant['checked_in_at'], participant['group_id'], participant['group_player_ids'],
                                 participant['id'], participant['name'], participant['tournament_id'], 
                                 participant['challonge_username'], participant['username'], participant['checked_in']))
        return l
    
    def add_participant(tournament_id, name):
        # check if the participant is already in the tournament
        partipants = challonge.participants.index(tournament_id)
        for p in partipants:
            if p['name'] == name:
               return "Participant already in the tournament"
        
        p = challonge.participants.create(tournament_id, name)
        return Participant(p['checked_in_at'], p['group_id'], p['group_player_ids'], p['id'], p['name'], p['tournament_id'], p['challonge_username'], p['username'], p['checked_in'])
    
    def remove_participant(self, tournament_id, participant_id):
        challonge.participants.destroy(tournament_id, participant_id)
    
    def start_tournament(self, tournament_id):
        challonge.tournaments.start(tournament_id)

    def randomize_participants(self, tournament_id):
        challonge.participants.randomize(tournament_id)
        
    def finalize_tournament(self, tournament_id):
        challonge.tournaments.finalize(tournament_id)
        
    def update_format(self, tournament_id, player_count, set_double = False):
        
        # get current tournament type
        t = challonge.tournaments.show(tournament_id)
        t_type = t['tournament_type']
        new_type = ""
        if player_count < 17:
            t_type = "round robin"
        elif player_count > 32 and player_count < 80 and set_double:
            t_type = "double elimination"
        elif player_count > 79 and player_count < 121 and set_double:
            t_type = "double elimination"
        elif player_count > 16 and player_count < 65:
            t_type = "swiss"
        elif player_count > 80 and player_count < 160:
            t_type = "single elimination"
        else:
            t_type = "single elimination"
        
        params = {
            "tournament_type": t_type
        }        
        challonge.tournaments.update(tournament_id, **params)
        
    
    
    