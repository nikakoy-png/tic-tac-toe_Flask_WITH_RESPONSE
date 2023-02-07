import datetime
import hashlib

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required, get_jwt_identity,
)

from flask_restful import Resource
from mongoengine import ValidationError

from MODEL.MongoEngineMODELS import User, Game, TokenBlocklist


class CreateGameAPI(Resource):
    def post(self):
        body = request.get_json()
        player_1 = User.objects.get(username=body['player_1'])
        player_2 = User.objects.get(username=body['player_2'])
        if not player_1.search_game_status and not player_2.search_game_status:
            print("Not search")
        hash_code = hashlib.sha256((str(player_1) + str(player_2) + str(datetime.datetime.now(datetime.timezone.utc)))
                                   .encode('utf-8')).hexdigest()
        game = Game(player_1=player_1, player_2=player_2, hash_code=hash_code, move_player=player_1)
        game.save()
        player_1.update(set__search_game_status=False)
        player_2.update(set__search_game_status=False)
        player_1.save()
        player_2.save()
        return (
            {
                "game_code": hash_code,
            },
            200
        )


# transfer from this file to services

# decorator for check diagonal
# def decorator_check_for_winner(func):
#     def wrapper_acc_arg(state):
#         for player in [1, -1]:
#             for index in [0, 0]:
#                 if state[index][index] == player and \
#                         state[index + 1][index + 1] == player and \
#                         state[index + 2][index + 2] == player:
#                     return player
#                 if state[index][index + 2] == player and \
#                         state[index + 1][index + 1] == player and \
#                         state[index+2][index] == player:
#                     return player
#         func(state)
#     return wrapper_acc_arg


# @decorator_check_for_winner
def check_state_for_winner(state: list[list]):
    for player in [1, -1]:
        for y in range(len(state)):
            # check Ox
            if state[y][y] == player and state[y][1] == player and state[y][2] == player:
                return player
            # check Oy
            if state[0][y] == player and state[1][y] == player and state[2][y] == player:
                return player
            if state[0][0] == player and \
                    state[0 + 1][0 + 1] == player and \
                    state[0 + 2][0 + 2] == player:
                return player
            if state[0][0 + 2] == player and \
                    state[0 + 1][0 + 1] == player and \
                    state[0 + 2][0] == player:
                return player
    return None


class UpdStateGame(Resource):
    def post(self):
        body = request.get_json()
        game = Game.objects.get(hash_code=body['hash_code'])
        state = game.state_game
        # replace  ==  because .username -- is wrong
        if body['player'] == game.move_player.username and state[int(body['move'] / 3)][(body['move'] % 3)] == 0:
            state[int(body['move'] / 3)][(body['move'] % 3)] = 1 if (game.player_1 == game.move_player) else -1
            game.update(set__state_game=state)
            game.update(set__move_player=game.player_1 if (game.player_2 == game.move_player) else game.player_2)
            game.save()

            winner = check_state_for_winner(state)

            if winner is not None:
                winner = game.player_1 if winner == 1 else game.player_2
                loser = game.player_1 if winner == -1 else game.player_2
                game.update(set__winner=winner)
                game.save()
                loser.update(set__losses=(loser.losses + 1))
                winner.update(set__victories=(winner.victories + 1))
                winner.update(set__rating=(winner.rating + 10))
                winner.save()
                loser.save()
                return (
                    {
                        "message": "Game is end!",
                        "winner": winner.username
                    },
                    200
                )
        for line in state:
            if 0 in line:
                return (
                    {
                        "message": True,
                    },
                    200
                )
        game.update(set__winner=None)
        game.update(set__move_player=None)
        game.save()
        return (
            {
                "message": "Game is end! Full plays",
                "winner": None
            },
            200
        )
    # make try except (and about request with 'move' == > 8 and < 0)
