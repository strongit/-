# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the auth module of user package,
# using to user authutification including
# authentication(login by user&password, login by token),
# autherization(privilege auth by token, etc.)
#

from flask import g, request
from flask_restful import reqparse, Resource
from .models import User
# , Privilege, Role
from .. import app, utils
from . import utils as userUtils
# serializer for JWT
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# exceptions for JWT
from itsdangerous import SignatureExpired, BadSignature, BadData
import datetime
import time


class TokenAPI(Resource):
    """
    authentification of token
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(TokenAPI, self).__init__()

    """
    user login or token refresh, return access token.
    determited by granttype:
    * login: request with username & password, return access token
      & refresh token.
    * refreshtoken: request with refreshtoken, return access token.
    """
    def post(self):
        args = self.argCheckForPost()

        if args['granttype'] == 'login':
            # use username and password to login and get token
            [token, refreshToken, user, last_login, msg] = AuthMethods.login(
                args['username'], args['password'])
            if token:
                app.logger.info(utils.logmsg(msg))
                msg = 'user logged in.<user:' + user.username + '>'
                response = {"message": msg,
                            "token": token,
                            "refreshtoken": refreshToken,
                            "user_info": user.getDictInfo()}
                return response, 200
            # rewrite the msg, we do not tell them too mutch:)
            msg = 'wrong username & password'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)

        elif args['granttype'] == 'refreshtoken':
            # use refresh token to get a new access token
            [token, msg] = AuthMethods.tokenRefresh(args['refreshtoken'])
            if not token:
                app.logger.info(utils.logmsg(msg))
                raise utils.InvalidAPIUsage(msg)
            response = {"message": msg, "token": token}
            return response, 200

        else:
            # error happen
            return {"message": 'wrong grant_type.'}, 500

    """
    use token to authentification, return user info
    """
    def get(self):
        token = self.argCheckForGet()
        # verify the token
        [user_id, priv_name_list, msg] = AuthMethods.tokenAuth(token)
        if not user_id:
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        else:
            user = User.getValidUser(user_id=user_id)
            if not user:
                msg = "cannot find user when autherization"
                app.logger.info(utils.logmsg(msg))
                raise utils.InvalidAPIUsage(msg)
        # we don't tell too much so rewrite the message
        msg = "user logged in.<username:" + user.username + ">"
        response = {"message": msg,
                    "token": token,
                    "user_info": user.getDictInfo()}
        app.logger.debug(utils.logmsg(msg))
        return response, 200

    def put(self):
        """
        modf token owner userinfo
        """
        [target_user, username, hashed_password, tel, email] = \
            self.argCheckForPut()
        # update user
        target_user.update(
            username=username, hashed_password=hashed_password,
            tel=tel, email=email)
        target_user.save()
        msg = 'current user info updated.'
        app.logger.info(msg)
        response = {"message": msg, "user_id": target_user.user_id}
        return response, 200

    def argCheckForPost(self):
        self.reqparse.add_argument(
            'granttype', type=str, location='json',
            required=True, help='granttype must be "refreshtoken/login"')
        args = self.reqparse.parse_args()
        grant_type = args['granttype']
        if grant_type == 'login':
            # need username and password to login
            self.reqparse.add_argument(
                'username', type=str, location='json',
                required=True, help='user name must be string')
            self.reqparse.add_argument(
                'password', type=str, location='json',
                required=True, help='password must be string')
            args = self.reqparse.parse_args()
            return args
        elif grant_type == 'refreshtoken':
            # need refresh token to refresh token
            self.reqparse.add_argument(
                'refreshtoken', type=str, location='json',
                required=True, help='refreshtoken must be a string')
            args = self.reqparse.parse_args()
            return args
        else:
            raise utils.InvalidAPIUsage(
                'granttype must be "refreshtoken"/"login"')

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'token', type=str, location='headers',
            required=True, help='token must be string')
        args = self.reqparse.parse_args()
        token = args['token']
        return token

    def argCheckForPut(self):
        # verify the token
        token = self.argCheckForGet()

        [user_id, priv_name_list, msg] = AuthMethods.tokenAuth(token)
        if not user_id:
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        else:
            target_user = User.getValidUser(user_id=user_id)
            if not target_user:
                msg = "cannot find user when autherization"
                app.logger.info(utils.logmsg(msg))
                raise utils.InvalidAPIUsage(msg)

        # check other argument
        self.reqparse.add_argument(
            'username', type=str, location='json',
            help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            help='password must be string')
        self.reqparse.add_argument(
            'tel', type=str, location='json',
            help='tel must be str')
        self.reqparse.add_argument(
            'email', type=str, location='json',
            help='email must be str')

        args = self.reqparse.parse_args()
        # required args check

        password = args['password']
        if password:
            hashed_password = userUtils.hash_pass(password)
        else:
            hashed_password = None

        tel = args['tel']
        email = args['email']

        username = args['username']
        if username:
            user = User.getValidUser(username=username)
            if user:
                msg = 'user name is in used.'
                raise utils.InvalidAPIUsage(msg)
        elif username is '':
            msg = 'user name should not be empty string.'
            raise utils.InvalidAPIUsage(msg)
        return [target_user, username, hashed_password, tel, email]


class AuthMethods(Resource):
    """
    some static methods for authentification.
    """
    def __init__(self, user=None):
        super(AuthMethods, self).__init__()

    """
    user auth and return user token
    """
    @staticmethod
    def login(username, password):
        user = User.getValidUser(username=username)
        if not user:
            msg = 'cannot find username:' + username
            app.logger.debug(utils.logmsg(msg))
            return [None, None, None, None, msg]
        if not userUtils.hash_pass(password) == user.hashed_password:
            msg = 'user name and password cannot match.'
            app.logger.debug(utils.logmsg(msg))
            return [None, None, None, None, msg]
        # generate token sequence
        # token expiration time is set in the config file
        # the value is set in seconds: (day,second,microsecond)
        token = AuthMethods.genTokenSeq(
            user, app.config['ACCESS_TOKEN_EXPIRATION'])
        # generate refresh_token
        refreshToken = AuthMethods.genTokenSeq(
            user, app.config['REFRESH_TOKEN_EXPIRATION'])
        msg = 'user (' + username + ') logged in.'
        # write the login time to db
        last_login = user.last_login
        user.last_login = datetime.datetime.now()
        user.save()
        app.logger.debug(utils.logmsg(msg))
        return [token, refreshToken, user, last_login, msg]

    """
    token is generated as the JWT protocol.
    JSON Web Tokens(JWT) are an open, industry standard RFC 7519 method
    """
    @staticmethod
    def genTokenSeq(user, expires):
        s = Serializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['AUTH_SALT'],
            expires_in=expires)
        timestamp = time.time()
        priv_name_list = user.getPrivilegeNameList()
        return s.dumps(
            {'user_id': user.user_id,
             'username': user.username,
             'priv': priv_name_list,
             'iat': timestamp})
        # The token contains userid, user role and the token generation time.
        # u can add sth more inside, if needed.
        # 'iat' means 'issued at'. claimed in JWT.

    @staticmethod
    def tokenAuth(token):
        # token decoding
        s = Serializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['AUTH_SALT'])
        try:
            data = s.loads(token)
            # token decoding faild
            # if it happend a plenty of times, there might be someone
            # trying to attact your server, so it should be a warning.
        except SignatureExpired:
            msg = 'token expired'
            app.logger.warning(utils.logmsg(msg))
            return [None, None, msg]
        except BadSignature, e:
            encoded_payload = e.payload
            if encoded_payload is not None:
                try:
                    s.load_payload(encoded_payload)
                except BadData:
                    # the token is tampered.
                    msg = 'token tampered'
                    app.logger.warning(utils.logmsg(msg))
                    return [None, None, msg]
            msg = 'badSignature of token'
            app.logger.warning(utils.logmsg(msg))
            return [None, None, msg]
        except:
            msg = 'wrong token with unknown reason.'
            app.logger.warning(utils.logmsg(msg))
            return [None, None, msg]
        if ('user_id' not in data) or ('priv' not in data):
            msg = 'illegal payload inside'
            app.logger.warning(utils.logmsg(msg))
            return [None, None, msg]
        msg = 'user(' + data['username'] + ') logged in by token.'
        app.logger.debug(utils.logmsg(msg))
        user_id = data['user_id']
        priv_name_list = data['priv']
        return [user_id, priv_name_list, msg]

    @staticmethod
    def tokenRefresh(refreshToken):
        # varify the refreshToken
        [user_id, priv_name_list, msg] = AuthMethods.tokenAuth(refreshToken)
        if user_id:
            user = User.getValidUser(user_id=user_id)
            if not user:
                msg = 'invalid refresh token with wrong user_id'
                app.logger.warning(utils.logmsg(msg))
                return [None, msg]
        else:
            msg = 'invalid refresh token missing user_id'
            app.logger.warning(msg)
            return [None, msg]

        token = AuthMethods.genTokenSeq(
            user, app.config['ACCESS_TOKEN_EXPIRATION'])
        msg = "token refreshed"
        app.logger.info(utils.logmsg(msg))
        return [token, msg]


class PrivilegeAuth(Resource):
    """
    This class is used tobe a decoretor for other methods to check the
    client's privilege by token.
    Your method's 'required privilege' should be set as an argument of this
    decoretor. And this 'required privilege' should have been in the
    'privilege' table.
    If your method's 'required privilege' is one of user's privileges,
    user will be allowed to access the method, otherwise not.
    ps. user's privilege is checked by his token.
    """
    def __init__(self, privilegeRequired):
        # argument 'privilegeRequired' is to set up your method's privilege
        # name
        self.privilege_required = privilegeRequired
        super(PrivilegeAuth, self).__init__()

    def __call__(self, fn):
        def wrapped(*args, **kwargs):
            token = request.headers.get('token')
            if not token:
                msg = "you need a token to access"
                raise utils.InvalidAPIUsage(msg)
            [user_id, priv_name_list, msg] = AuthMethods.tokenAuth(token)
            if not user_id:
                msg = msg + " when autherization"
                raise utils.InvalidAPIUsage(msg)
            else:
                current_user = User.getValidUser(user_id=user_id)
                if not current_user:
                    msg = "cannot find user when autherization"
                    raise utils.InvalidAPIUsage(msg)

            u_priv_name = unicode(self.privilege_required, "UTF-8")
            for priv_name in priv_name_list:
                if u_priv_name == priv_name:
                    g.current_user = current_user
                    return fn(*args, **kwargs)

            msg = "Privilege not Allowed."
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        return wrapped
