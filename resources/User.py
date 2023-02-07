import datetime
import asyncio
import time

from flask import request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required, get_jwt_identity,
)

from flask_restful import Resource
from mongoengine import ValidationError, NotUniqueError

from MODEL.MongoEngineMODELS import User, TokenBlocklist



class RegisterAPI(Resource):
    def post(self):
        for x in range(10):
            print(x)
            time.sleep(1)

        test = [1, 1, 1]
        print(len(test))
        print(range(len(test)))
        for x in range(len(test)):
            print(x)
        try:
            body = request.get_json()
            user = User(**body)
            user.hash_password()
            user.save()
            user.reload()
            access_token = create_access_token(
                identity=str(user.username), expires_delta=datetime.timedelta(hours=5)
            )

            refresh_token = create_refresh_token(
                identity=str(user.id), expires_delta=datetime.timedelta(hours=5)
            )

            resp = make_response({
                "access_token": access_token,
                "username": user.username,
            }, 200)

            resp.set_cookie("refresh_token", refresh_token)
            resp.set_cookie("access_token", "Bearer {}".format(access_token))

            return resp
        except ValidationError:
            return (
                {"message": "Some wont wrong!"},
                400
            )
        except NotUniqueError:
            return (
                {"message": "Username already taken!"},
                400
            )


class LoginAPI(Resource):
    def post(self):
        body = request.get_json()
        user = User.objects.get(username=body['username'])
        if not user.check_hash_password(body['password']):
            return None

        user.update(set__online=True)
        user.save()

        access_token = create_access_token(
            identity=str(user.username), expires_delta=datetime.timedelta(minutes=1)
        )
        refresh_token = create_refresh_token(
            identity=str(user.id), expires_delta=datetime.timedelta(hours=5)
        )
        refresh_cookie = [("Set-Cookie", "refresh_token={}".format(refresh_token))]

        return (
            {
                "access_token": access_token,
                "username": user.username,
            },
            200,
            refresh_cookie,
        )


class LogoutAPI(RegisterAPI):

    @jwt_required()
    def post(self):
        revoked_token = get_jwt()

        jti = revoked_token["jti"]
        owner = revoked_token["sub"]
        created_ts = int(revoked_token["iat"])
        expires_ts = int(revoked_token["exp"])

        created = datetime.datetime.utcfromtimestamp(created_ts).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        expires = datetime.datetime.utcfromtimestamp(expires_ts).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        user = User.objects.get(username=owner)
        now = datetime.datetime.now(datetime.timezone.utc)

        block_token = TokenBlocklist(
            jti=jti,
            created_on=created,
            expires_on=expires,
            revoked_on=now,
            revoked_by=user,
        )
        block_token.save()

        user.update(set__online=False)

        return {"message": "JWT revoked"}


# Make more
class getUserProfile_Myself(Resource):
    @jwt_required()
    def post(self):
        print(get_jwt_identity())
