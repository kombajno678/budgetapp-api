
import os
import json

from jose import jwt
from six.moves.urllib.request import urlopen
# six.moves.urllib.request
from functools import wraps
from flask import request, _request_ctx_stack


AUTH0_DOMAIN = str(os.environ.get('AUTH0_DOMAIN', ''))
API_IDENTIFIER = str(os.environ.get('API_IDENTIFIER', ''))
ALGORITHMS = ["RS256"]


# Error handler
# from: https://auth0.com/docs/quickstart/backend/python
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Format error response and append status code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    print('DEBUG > get_token_auth_header')
    print('DEBUG > request.headers = ' + str(request.headers))
    auth = request.headers.get("Authorization", None)
    print('DEBUG > auth = ' + str(auth))

    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        print('DEBUG > requires_auth')
        token = get_token_auth_header()
        print('DEBUG > requires_auth ,token = ' + str(token))

        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError({"code": "invalid_header",
                             "description":
                             "Invalid header. "
                             "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError({"code": "invalid_header",
                             "description":
                             "Invalid header. "
                             "Use an RS256 signed JWT Access Token"}, 401)

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience='https://dev-wkdk2hez.eu.auth0.com/api/v2/',
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )

            except Exception as err:
                print('error: ' + str(err))
                print('unverified_header : ' + str(unverified_header))
                raise AuthError({"code": "invalid_header (other error)",
                                 "err": str(err)}, 401)

            userId = payload.get('sub').split('|')[1]
            _request_ctx_stack.top.current_user = userId
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)
    return decorated
