'''
Collection of functions etc to make statistical model for predicting results of USAU games
'''

import networkx as nx
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np

class season(object):
    '''
    imports dict for season, calculates eigenvector-based rankings
    
    object should be a dict with at least 3 sub-dictionaries:
        tournaments
        games
        teams
        
     game objects (example):
        {u'id': u'FBexwtOZKtU5voJXjP4qcVKCQb78%2fMFqx%2f%2fEQBFEzZI',
        u'local_datetime': u'2016-02-20 12:00',
         u'location': {u'lat': 39.4014955, u'lng': -76.6019125},
         u'score': [10, 4],
         u'teams': [u'IUJChQN%2fVmdp1B9RpShOUjV5C5RU0oToBqnNS3qXQR0',
          u'eBfYTBsF2QnDRMs8V1yUN%2fp5IbHWtCxgflJOzvPklq8'],
         u'tournament': u'Leap-N-Layout-2016',
         u'weather': {u'apparentTemperature': 54.6,
          u'dewPoint': 34.79,
          u'humidity': 0.47,
          u'icon': u'clear-day',
          u'precipIntensity': 0,
          u'precipProbability': 0,
          u'pressure': 1016.35,
          u'summary': u'Clear',
          u'temperature': 54.6,
          u'time': 1455987600,
          u'visibility': 10,
          u'windBearing': 233,
          u'windSpeed': 7.37},
         u'windSpeed': 9.47}

     team objects:
        {'eigenvector_centrality': 0.0,
         u'id': u'Yn%2fie5WBSSBpoqfvTxQdCCJETGM4DAkX%2bKCmapPhFwk',
         u'name': u'Villanova (Hucking Halos)',
         'ranking': 270,
         u'usau_rating': None}

    '''
    
    def __init__(self, dict_object):
        self.tournaments = dict_object['tournaments']
        self.games = dict_object['games']
        self.teams = dict_object['teams']
        self.games_to_graph()
        self.rank_teams()
        self.LR = {}
        
        
    def games_to_graph(self):
        '''creates networkx directed graph object from games'''
        self.graph = nx.DiGraph()
        for team in self.teams.iterkeys():
            self.graph.add_node(team)
        for game in self.games.iterkeys():
            margin = self.games[game]['score'][0] - self.games[game]['score'][1]
            if margin > 0:
                winner_id = self.games[game]['teams'][0]
                loser_id = self.games[game]['teams'][1]
            else:
                winner_id = self.games[game]['teams'][1]
                loser_id = self.games[game]['teams'][0]
            self.graph.add_edge(loser_id,winner_id, 
                                            weight = abs(margin),
                                            attr_dict=self.games[game])
            
        cent = nx.eigenvector_centrality(self.graph)
        for team in cent.iterkeys():
            self.teams[team]['eigenvector_centrality'] = cent[team]
            
    def plot_graph(self):
        nx.draw_spring(self.graph)
        
    def rank_teams(self):
        ranked_team_ids = sorted(self.teams.keys(), key=lambda x: -self.teams[x]['eigenvector_centrality'])
        rank = 1
        for team in ranked_team_ids:
            self.teams[team]['ranking'] = rank
            rank += 1
            
    def games_to_LR(self):
        ''' 
        converts data into usable form for logistic regression:
                X: Ngames*Nfields array with various data from games
                y: Ngames*1 array, =True if 1st team ("home") wins game
        '''
        X = []
        y = []
        for game in self.games.itervalues():
            #print(game['weather'].keys())
            if self.teams[game['teams'][0]]['eigenvector_centrality'] < 1e-16:
                self.teams[game['teams'][0]]['eigenvector_centrality'] = 1e-16
            if self.teams[game['teams'][1]]['eigenvector_centrality'] < 1e-16:
                self.teams[game['teams'][1]]['eigenvector_centrality'] = 1e-16
                
            # treat teams[0] as winner, flow from 1->0
            delta_ec = np.log10(self.teams[game['teams'][0]]['eigenvector_centrality']) - np.log10(self.teams[game['teams'][1]]['eigenvector_centrality'])
            ''' ignore flow values for now
            flow_val_10 = nx.maximum_flow_value(self.graph,
                game['teams'][1],game['teams'][0], 
                capacity='weight')
            flow_val_01 = nx.maximum_flow_value(self.graph,
                game['teams'][0],game['teams'][1], 
                capacity='weight')
            '''
            try:
                X.append([delta_ec])
                y.append(game['score'][0] - game['score'][1] > 0)
                # also append complement so that data is symmetric
                X.append([-delta_ec])
                y.append(game['score'][1] - game['score'][0] > 0)
            except Exception,e:
                print('Game: ' + str(game['id']) + '; ' + str(e))
        
        self.LR['X'] = np.array(X)
        self.LR['y'] = np.array(y)
            