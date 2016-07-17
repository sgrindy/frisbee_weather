'''
Collection of functions etc to make statistical model for predicting results of USAU games
'''

import networkx as nx
import matplotlib.pyplot as plt

class season(object):
    '''
    imports dict for season, calculates eigenvector-based rankings
    
    object should be a dict with at least 3 sub-dictionaries:
        tournaments
        games
        teams
    '''
    
    def __init__(self, dict_object):
        self.tournaments = dict_object['tournaments']
        self.games = dict_object['games']
        self.teams = dict_object['teams']
        self.games_to_graph()
        
        
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
            self.graph.add_edge(loser_id,winner_id)
            
        cent = nx.eigenvector_centrality(self.graph)
        for team in cent.iterkeys():
            self.teams[team]['eigenvector_centrality'] = cent[team]
            
    def plot_graph(self):
        nx.draw_spring(self.graph)