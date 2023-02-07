from resources.User import *
from resources.Game import *


def init_router(api):
    api.add_resource(RegisterAPI, "/api/auth/signup")
    api.add_resource(LoginAPI, "/api/auth/login")
    api.add_resource(LogoutAPI, "/api/auth/logout")
    api.add_resource(getUserProfile_Myself, "/api/profile")
    api.add_resource(CreateGameAPI, "/api/create-game")
    api.add_resource(UpdStateGame, "/api/update-state-game")
