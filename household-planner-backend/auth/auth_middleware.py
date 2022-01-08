from starlette.authentication import AuthenticationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from firebase_admin import auth

CREDENTIALS_TYPE = 'Bearer'
CREDENTIALS_HEADER_NAME = 'Authorization'


class AuthMiddleware(BaseHTTPMiddleware):
    default_error_message = 'unauthorized'

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == 'OPTIONS':
            return await call_next(request)

        try:
            user_email = self.authenticate_token(request)
        except AuthenticationError:
            return self.on_error()

        request.state.user_email = user_email
        return await call_next(request)

    def authenticate_token(self, request: Request):
        auth_header = request.headers.get(CREDENTIALS_HEADER_NAME)
        if not auth_header:
            raise AuthenticationError(self.default_error_message)

        scheme, credentials = auth_header.split()
        if scheme.lower() != CREDENTIALS_TYPE.lower():
            raise AuthenticationError(self.default_error_message)

        try:
            firebase_token = auth.verify_id_token(credentials)
        except:
            raise AuthenticationError(self.default_error_message)

        user_email = firebase_token.get('email')
        print(user_email)

        return user_email

    def on_error(self):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
