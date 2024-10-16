import os.path
import json
import asyncio
import google.auth

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import secretmanager
from qasync import asyncSlot
from GUI.loading import Loading

from google_auth_oauthlib.flow import InstalledAppFlow

from google.oauth2 import service_account

class BTMAppSheets:
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    SHEET_ID = ""
    creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/drive'])

    def __init__(self, sheet_id, service):
        self.SHEET_ID = sheet_id
        self.service = service

    @asyncSlot()
    async def get_sheet_names(self):
        try:
            sheet = self.service.spreadsheets()
            request = sheet.get(spreadsheetId=self.SHEET_ID)
            result = await asyncio.to_thread(request.execute)
            sheets = result.get("sheets", [])
        
            sheet_names = []
            for sheet in sheets:
                sheet_names.append(sheet['properties']['title'])
            return sheet_names
        except HttpError as e:
            print(f"An error occurred: {e}") 

    @asyncSlot()
    async def get_headers(self, sheetname):
        try:
            sheet = self.service.spreadsheets()
            request = sheet.values().get(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname))
            result = await asyncio.to_thread(request.execute)
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return
            else:
                return values[0]
        except HttpError as e:
            print(f"An error occurred: {e}")
            
    @asyncSlot()
    async def get_sheet(self, sheetname):  
        try:
            sheet = self.service.spreadsheets()
            request = sheet.values().get(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname))
            result = await asyncio.to_thread(request.execute)
            values = result.get("values", [])
            
        
            if not values:
                print("No data found.")
                return
            else:
                # expected header names
                expected_headers = ['Rank', 'Blader', 'Wins' 'Losses', 
                                    '1st', '2nd', '3rd', 'Points', 'Win%',
                                    'Rating', 'Region', 'Column 1', 'Column 2',
                                    'Column 3', 'Column 4', 'Column 5', 'Column 6',
                                    'Column 7', 'Column 8', 'Column 9']
                
                # get the header row
                header_row = None
                for row in values:
                    for row_value in row:
                        if row_value in expected_headers:
                            header_row = row
                            break
                if header_row is None:
                    raise ValueError("Expected headers not found in the sheet")
                # return list of values minus the header row

                return values
        except HttpError as e:
            print(f"An error occurred: {e}")
    
    # Create a new sheet with the given name
    @asyncSlot()
    async def create_sheet_empty(self, sheetname):
        try:
            body = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": sheetname
                        }
                    }
                }]
            }

            result = await asyncio.to_thread(self.service.spreadsheets().batchUpdate(spreadsheetId=self.SHEET_ID, body=body).execute)
            
            
        
            # Update header row
            headers = ['Rank', 'Blader', 'Wins', 'Losses', 
                                    '1st', '2nd', '3rd', 'Points', 'Win%',
                                    'Rating', 'Region', 'Column 1', 'Column 2',
                                    'Column 3', 'Column 4', 'Column 5', 'Column 6',
                                    'Column 7', 'Column 8', 'Column 9']
            

            
            values = [headers]
            body = {
                "values": values
            }

            result = await asyncio.to_thread(self.service.spreadsheets().values().update(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname), valueInputOption="RAW", body=body).execute)
        except HttpError as e:
            print(f"An error occurred: {e}")
    
    # Create a new sheet with the given name and existing players           
    @asyncSlot()
    async def create_sheet(self, sheetname, players, groups = None): 
        try:
            body = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": sheetname
                        }
                    }
                }]
            }

            result = await asyncio.to_thread(self.service.spreadsheets().batchUpdate(spreadsheetId=self.SHEET_ID, body=body).execute)
            
              # Update header row
            headers = ['Rank', 'Blader', 'Wins', 'Losses', 
                                    '1st', '2nd', '3rd', 'Points', 'Win%',
                                    'Rating', 'Region', 'Column 1', 'Column 2',
                                    'Column 3', 'Column 4', 'Column 5', 'Column 6',
                                    'Column 7', 'Column 8', 'Column 9']            

            
            values = [headers]
            body = {
                "values": values
            }
            
          
            # if we have groups, add an additional row above the inital header saying Group A

            if groups is not None:
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A2:T"
                                                         .format(sheetname), valueInputOption="RAW", body=body).execute)
                group_row = ['Group A']
                values = [group_row]
                body = {
                    "values": values
                }
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A1:T"
                                                         .format(sheetname), valueInputOption="RAW", body=body).execute)
        
                # Start from A3
                first_row = 3
                next_row = first_row
                values = []
                group_a = players[0]
                for player in group_a:
                    rank_formula = '=RANK(J%s,J$%s:J$%s,0)' % (next_row, first_row, first_row + len(group_a))
                    points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (next_row, next_row, next_row, next_row)
                    win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (next_row, next_row, next_row)
                    raiting_formula = '=ROUND((H%s * 100) * I%s)' % (next_row, next_row)
                    values.append([rank_formula, player.get_name(), player.get_wins(), player.get_losses(),
                                player.get_first(), player.get_second(), player.get_third(), points_formula,
                                win_percentage_formula, raiting_formula, player.get_region()])
                    next_row += 1
                
                body = {
                    "values": values
                }                    
                await asyncio.to_thread(self.service.spreadsheets().values()
                                        .update(spreadsheetId=self.SHEET_ID, range="{}!A{}:T"
                                                .format(sheetname, first_row), valueInputOption="USER_ENTERED", body=body)
                                        .execute)

                group_row = ['Group B']
                values = [group_row]
                body = {
                    "values": values
                }
                next_row = next_row + 2
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A{}:T"
                                                         .format(sheetname, next_row), valueInputOption="RAW", body=body)
                                                 .execute)

                values = [headers]
                body = {
                    "values": values
                }

                next_row = next_row + 1
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A{}:T"
                                                         .format(sheetname, next_row), valueInputOption="RAW", body=body)
                                                 .execute)

                first_row = next_row + 1
                next_row = first_row
                group_b = players[1]
                values = []
                for player in group_b:
                    rank_formula = '=RANK(J%s,J$%s:J$%s,0)' % (next_row, first_row, first_row + len(group_b))
                    points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (next_row, next_row, next_row, next_row)
                    win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (next_row, next_row, next_row)
                    raiting_formula = '=ROUND((H%s * 100) * I%s)' % (next_row, next_row)
                
                    values.append([rank_formula, player.get_name(), player.get_wins(), player.get_losses(),
                                player.get_first(), player.get_second(), player.get_third(), points_formula,
                                win_percentage_formula, raiting_formula, player.get_region()])
                
                    next_row += 1
                

                body = {
                    "values": values
                }

                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A{}:T"
                                                         .format(sheetname, first_row), valueInputOption="USER_ENTERED"
                                                         , body=body)
                                                 .execute)

                group_row = ["Finals"]
                values = [group_row]
                body = {
                    "values": values
                }
                next_row = next_row + 2
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A{}:T"
                                                         .format(sheetname, next_row), valueInputOption="RAW"
                                                         , body=body).execute)

                values = [headers]
                body = {
                    "values": values
                }

                next_row = next_row + 1
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A{}:T"
                                                         .format(sheetname, next_row), valueInputOption="RAW"
                                                         , body=body)
                                                 .execute)


                if len(players) > 2:
                    first_row = next_row + 1
                    next_row = first_row
                    finals = players[2]
                    if len(finals) > 0:
                        values = []
                        for player in finals:
                            rank_formula = '=RANK(J%s,J$%s:J$%s,0)' % (next_row, first_row, first_row + len(finals))
                            points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (next_row, next_row, next_row, next_row)
                            win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (next_row, next_row, next_row)
                            raiting_formula = '=ROUND((H%s * 100) * I%s)' % (next_row, next_row)
                        
                            values.append([rank_formula, player.get_name(), player.get_wins(), player.get_losses(),
                                        player.get_first(), player.get_second(), player.get_third(), points_formula,
                                        win_percentage_formula, raiting_formula, player.get_region()])
                        
                            next_row += 1

                        body = {
                            "values": values
                        }

                        result = await asyncio.to_thread(self.service.spreadsheets()
                                                         .values().update(spreadsheetId=self.SHEET_ID
                                                                          , range="{}!A{}:T".format(sheetname, first_row)
                                                                          , valueInputOption="USER_ENTERED", body=body)
                                                         .execute)

            else:  
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A1:T"
                                                         .format(sheetname), valueInputOption="RAW"
                                                         , body=body)
                                                 .execute)
                # Update player data after header row and adjust formulas to be the correct row              
                values = []
                
                for player in players:
                    
                    rank_formula = '=RANK(J%s,J$2:J$400,0)' % (next_row)
                    points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (next_row, next_row, next_row, next_row)
                    win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (next_row, next_row, next_row)
                    raiting_formula = '=ROUND((H%s * 100) * I%s)' % (next_row, next_row)
                    
                    values.append([rank_formula, player.get_name(), player.get_wins(), player.get_losses(),
                                    player.get_first(), player.get_second(), player.get_third(), points_formula,
                                    win_percentage_formula, raiting_formula, player.get_region()])
                    
                    next_row += 1
                
                
                body = {
                    "values": values
                }
    
                
                
                
                result = await asyncio.to_thread(self.service.spreadsheets().values()
                                                 .update(spreadsheetId=self.SHEET_ID, range="{}!A2:T"
                                                         .format(sheetname), valueInputOption="USER_ENTERED"
                                                         , body=body)
                                                 .execute)
            
        except HttpError as e:
            print(f"An error occurred: {e}")
    
    @asyncSlot()
    async def add_player(self, sheetname, player):
        try:
            # Get the header row and and store the row number of the next empty row
            next_row = len(self.get_sheet(sheetname)) + 1
            
            # Update player data after header row and adjust formulas to be the correct row              
            values = []
            
            rank_formula = '=RANK(J%s,J$2:J$400,0)' % (next_row)
            points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (next_row, next_row, next_row, next_row)
            win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (next_row, next_row, next_row)
            raiting_formula = '=ROUND((H%s * 100) * I%s)' % (next_row, next_row)
            
            values.append([rank_formula, player.get_name(), player.get_wins(), player.get_losses(),
                            player.get_first(), player.get_second(), player.get_third(), points_formula,
                            win_percentage_formula, raiting_formula, player.get_region()])
            
            body = {
                "values": values
            }
            
            result = await asyncio.to_thread(self.service.spreadsheets().values()
                                             .append(spreadsheetId=self.SHEET_ID, range="{}!A2:T"
                                                     .format(sheetname), valueInputOption="USER_ENTERED"
                                                     , body=body)
                                             .execute)
        except HttpError as e:
            print(f"An error occurred: {e}")
    
    @asyncSlot()
    async def remove_player(self, sheetname, player):
        try:
            # Find the row number that contains the player
            result = await asyncio.to_thread(self.service.spreadsheets().values()
                                             .get(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname))
                                             .execute)
            values = result.get("values", [])
            
            player_row = None
            for row in values:
                if row[1] == player:
                    player_row = values.index(row)
                    break
            
            # Remove the player from the sheet and reformat the sheet adjusting the formulas and ignoring header row
            values.pop(player_row)
            
            for row in values:
                
                # Check if the row is the header row
                if row[0] == "Rank":
                    continue
                
                rank_formula = '=RANK(J%s,J$2:J$400,0)' % (values.index(row) + 1)
                points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (values.index(row) + 1, values.index(row) + 1, values.index(row) + 1, values.index(row) + 1)
                win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (values.index(row) + 1, values.index(row) + 1, values.index(row) + 1)
                raiting_formula = '=ROUND((H%s * 100) * I%s)' % (values.index(row) + 1, values.index(row) + 1)
                
                row[0] = rank_formula
                row[7] = points_formula
                row[8] = win_percentage_formula
                row[9] = raiting_formula

            body = {
                "values": values
            }
        
            
            result = await asyncio.to_thread(self.service.spreadsheets().values()
                                             .update(spreadsheetId=self.SHEET_ID, range="{}!A1:T"
                                                     .format(sheetname), valueInputOption="USER_ENTERED"
                                                     , body=body)
                                             .execute)
            
            
        except HttpError as e:
            print(f"An error occurred")
        
    @asyncSlot()
    async def update_player(self, sheetname, winner, loser, group = None):
        try:
            sheet = self.service.spreadsheets()
            result = await asyncio.to_thread(sheet.values().get(spreadsheetId=self.SHEET_ID, range="{}!A1:T"
                                                                .format(sheetname))
                                             .execute)
            values = result.get("values", [])
            
            # Get the row number that contains winner name and loser name
            winner_row = None
            loser_row = None
            for row in values:
                if row[1] == winner:
                    winner_row = values.index(row)
                if row[1] == loser:
                    loser_row = values.index(row)
            
            # Update the wins and losses for the winner and loser
            winner_wins = int(values[winner_row][2]) + 1
            loser_losses = int(values[loser_row][3]) + 1
            
            # ensure formulas are still in place for winner
            rank_formula = '=RANK(J%s,J$2:J$400,0)' % (winner_row + 1)
            points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (winner_row + 1, winner_row + 1, winner_row + 1, winner_row + 1)
            win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (winner_row + 1, winner_row + 1, winner_row + 1)
            raiting_formula = '=ROUND((H%s * 100) * I%s)' % (winner_row + 1, winner_row + 1)
            
            # Set the values for the formulas
            values[winner_row][0] = rank_formula
            values[winner_row][7] = points_formula
            values[winner_row][8] = win_percentage_formula
            values[winner_row][9] = raiting_formula
            
            # ensure formulas are still in place for loser
            rank_formula = '=RANK(J%s,J$2:J$400,0)' % (loser_row + 1)
            points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (loser_row + 1, loser_row + 1, loser_row + 1, loser_row + 1)
            win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (loser_row + 1, loser_row + 1, loser_row + 1)
            raiting_formula = '=ROUND((H%s * 100) * I%s)' % (loser_row + 1, loser_row + 1)
            
            # Set the values for the formulas
            values[loser_row][0] = rank_formula
            values[loser_row][7] = points_formula
            values[loser_row][8] = win_percentage_formula
            values[loser_row][9] = raiting_formula
                        
            # Push the new data to the sheet
            values[winner_row][2] = winner_wins
            values[loser_row][3] = loser_losses
            
            body = {
                "values": values
            }
            
            result = await asyncio.to_thread(self.service.spreadsheets().values()
                                             .update(spreadsheetId=self.SHEET_ID, range="{}!A1:T"
                                                     .format(sheetname), valueInputOption="USER_ENTERED"
                                                     , body=body)
                                             .execute)
            
        except HttpError as e:
            print(f"An error occurred: {e}")
    
    @asyncSlot()
    async def undo_update_player(self, sheetname, winner, loser):
        try:
            sheet = self.service.spreadsheets()
            result = await asyncio.to_thread(sheet.values().get(spreadsheetId=self.SHEET_ID, range="{}!A1:T"
                                                                .format(sheetname))
                                             .execute)
            values = result.get("values", [])
            
            # Get the row number that contains winner name and loser name
            winner_row = None
            loser_row = None
            for row in values:
                if row[1] == winner:
                    winner_row = values.index(row)
                if row[1] == loser:
                    loser_row = values.index(row)
            
            # Update the wins and losses for the winner and loser
            if int(values[winner_row][2]) != 0:
                winner_wins = int(values[winner_row][2]) - 1
            
            if int(values[loser_row][3]) != 0:
                loser_losses = int(values[loser_row][3]) - 1
            
            # ensure formulas are still in place for winner
            rank_formula = '=RANK(J%s,J$2:J$400,0)' % (winner_row + 1)
            points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (winner_row + 1, winner_row + 1, winner_row + 1, winner_row + 1)
            win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (winner_row + 1, winner_row + 1, winner_row + 1)
            raiting_formula = '=ROUND((H%s * 100) * I%s)' % (winner_row + 1, winner_row + 1)
            
            # Set the values for the formulas
            values[winner_row][0] = rank_formula
            values[winner_row][7] = points_formula
            values[winner_row][8] = win_percentage_formula
            values[winner_row][9] = raiting_formula
            
            # ensure formulas are still in place for loser
            rank_formula = '=RANK(J%s,J$2:J$400,0)' % (loser_row + 1)
            points_formula = '=SUM(C%s,(E%s*3),(F%s*2),(G%s*1))' % (loser_row + 1, loser_row + 1, loser_row + 1, loser_row + 1)
            win_percentage_formula = '=IFERROR(ROUND((C%s/(C%s+D%s)), 2), "")' % (loser_row + 1, loser_row + 1, loser_row + 1)
            raiting_formula = '=ROUND((H%s * 100) * I%s)' % (loser_row + 1, loser_row + 1)
            
            # Set the values for the formulas
            values[loser_row][0] = rank_formula
            values[loser_row][7] = points_formula
            values[loser_row][8] = win_percentage_formula
            values[loser_row][9] = raiting_formula
                        
            # Push the new data to the sheet
            values[winner_row][2] = winner_wins
            values[loser_row][3] = loser_losses
            
            body = {
                "values": values
            }
            
            result = await asyncio.to_thread(self.service.spreadsheets().values()
                                             .update(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname)
                                                     , valueInputOption="USER_ENTERED", body=body)
                                             .execute)
            
        except HttpError as e:
            print(f"An error occurred: {e}")
          
    @asyncSlot()
    async def check_sheet_exists(self, sheetname):
        try:
            sheet = self.service.spreadsheets()
            result = await asyncio.to_thread(sheet.get(spreadsheetId=self.SHEET_ID).execute)
            sheets = result.get("sheets", [])
        
            for sheet in sheets:
                if sheet['properties']['title'] == sheetname:
                    return True
            return False
        except HttpError as e:
            print(f"An error occurred: {e}") 
            return False