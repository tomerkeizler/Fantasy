from flask import Flask, jsonify, make_response, send_from_directory
from flask import request
from os.path import exists, join
from bson.json_util import dumps

import mongo
from create_team import create_team
from constants import CONSTANTS
from sample_data import sample_data
from sample_data import team_constraints
from players_statistics import players_statistics


app = Flask(__name__, static_folder='build')


###############################################################
####### ENDPOINTS - STATOSTICS #######
###############################################################

@app.route(CONSTANTS['ENDPOINT']['PLAYER_STATS'], methods=['POST'])
def get_players_stats():
    data = request.get_json()
    return jsonify(players_statistics.get_players_statistics(data['year']))

########################################
####### ENDPOINTS - MY TEAM PAGE #######
########################################

@app.route(CONSTANTS['ENDPOINT']['MY_TEAM'], methods = ['POST'])
def get_final_team():
    data = request.get_json()
    list_player_id = []
    for player in team_constraints['player_selection']['player_list']:
        list_player_id.insert(0, player['player_id'])
    fantasy_league_and_defeated_players = create_team.get_used_players(data['year'], data['round'], list_player_id)
    fantasy_league = fantasy_league_and_defeated_players['choosen']
    # defeated players = fantasy_league_and_defeated_players['defeated']
    return jsonify(fantasy_league)

###############################################################
####### ENDPOINTS - TEAM CONSTRAINTS - FORMATION PICK #######
###############################################################

# @app.route(CONSTANTS['ENDPOINT']['TEAM_CONSTRAINTS']['FORMATION_PICK'])
# def get_formation_pick_constraint_data():
#.............


# @app.route(CONSTANTS['ENDPOINT']['TEAM_CONSTRAINTS']['FORMATION_PICK'], methods = ['POST'])
# def update_formation_pick_constraint_data():
#.............

###############################################################
####### ENDPOINTS - TEAM CONSTRAINTS - PLAYER SELECTION #######
###############################################################

@app.route(CONSTANTS['ENDPOINT']['TEAM_CONSTRAINTS']['PLAYER_SELECTION'])
def get_player_selection_constraint_data():
    return jsonify(team_constraints['player_selection']['player_list'])


@app.route(CONSTANTS['ENDPOINT']['TEAM_CONSTRAINTS']['PLAYER_SELECTION'], methods = ['POST'])
def update_player_selection_constraint_data():
    data = request.get_json()
    team_constraints['player_selection']['player_list'].clear()
    for playerSelected in data['playerSelectionConstraintList']:
        team_constraints['player_selection']['player_list'].insert(0, playerSelected)
    return make_response('', CONSTANTS['HTTP_STATUS']['201_CREATED'])


@app.route(CONSTANTS['ENDPOINT']['TEAM_CONSTRAINTS']['TEAM_FILTER'])
def get_all_teams():
    teams = mongo.find_from_collection(mongo.teams_collection, {})
    return dumps(teams)
    

@app.route(CONSTANTS['ENDPOINT']['TEAM_CONSTRAINTS']['PLAYER_FILTER'], methods = ['POST'])
def get_squad_by_team():
    data = request.get_json()
    players_by_team = mongo.find_from_collection(mongo.players_data_collection, {'team_id': { '$in' : data['teams_id'] }})
    return dumps(players_by_team)

#######################
####### GENERAL #######
#######################

# @app.route(CONSTANTS['ENDPOINT']['LIST'] + '/<int:id>', methods=['DELETE'])
# def delete_list_item(id):
#     list_items_to_remove = [list_item for list_item in sample_data['list_text_assets']['list_items'] if list_item['_id'] == id]
#     if not list_items_to_remove:
#         json_response = jsonify({'error': 'Could not find an item with the given id'})
#         return make_response(json_response, CONSTANTS['HTTP_STATUS']['404_NOT_FOUND'])
#     if len(list_items_to_remove) > 1:
#         json_response = jsonify({'error': 'More than one list items found with the same id'})
#         return make_response(json_response, CONSTANTS['HTTP_STATUS']['500_INTERNAL_SERVER_ERROR'])
#     sample_data['list_text_assets']['list_items'] = [list_item for list_item in sample_data['list_text_assets']['list_items'] if list_item['_id'] != id]
#     return jsonify({'_id': id, 'text': 'This comment was deleted'})


# MasterDetail Page Endpoint
@app.route(CONSTANTS['ENDPOINT']['MASTER_DETAIL'])
def get_master_detail():
    return jsonify(sample_data['text_assets'])


# Catching all routes
# This route is used to serve all the routes in the frontend application after deployment.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    file_to_serve = path if path and exists(join(app.static_folder, path)) else 'index.html'
    return send_from_directory(app.static_folder, file_to_serve)


# Error Handler
@app.errorhandler(404)
def page_not_found(error):
    json_response = jsonify({'error': 'Page not found'})
    return make_response(json_response, CONSTANTS['HTTP_STATUS']['404_NOT_FOUND'])


if __name__ == '__main__':
    app.run(port=CONSTANTS['PORT'])
