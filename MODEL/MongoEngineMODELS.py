import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
import mongoengine as me
from mongoengine import ValidationError, DoesNotExist


class User(me.Document):
    # def _not_eq_username(val):
    # try:
    #     if User.objects.get(username=val):
    #         raise ValidationError('This name is taken!')
    # except DoesNotExist:
    #     return None

    username = me.StringField(unique=True)
    email = me.EmailField()
    password = me.StringField()
    create_date = me.DateTimeField(default=datetime.datetime.utcnow)
    roles = me.ListField(me.StringField(), default=['user'])
    online = me.BooleanField(default=False)
    search_game_status = me.BooleanField(default=False)
    rating = me.IntField(default=0)
    victories = me.IntField(default=0)
    losses = me.IntField(default=0)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode("utf8")

    def check_hash_password(self, password):
        return check_password_hash(self.password, password)


class Game(me.Document):
    player_1 = me.ReferenceField('User')
    player_2 = me.ReferenceField('User')
    # Means state fields tic-tac-toe
    state_game = me.ListField(default=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    create_date = me.DateTimeField(default=datetime.datetime.utcnow)
    hash_code = me.StringField()
    winner = me.ReferenceField('User', null=False)
    move_player = me.ReferenceField('User', null=False)


class TokenBlocklist(me.Document):
    jti = me.StringField(max_length=36, null=False)
    created_on = me.DateTimeField(null=False)
    expires_on = me.DateTimeField(null=False)
    revoked_on = me.DateTimeField(null=False)
    revoked_by = me.ReferenceField("User")


User.register_delete_rule(TokenBlocklist, "revoked_by", me.CASCADE)
