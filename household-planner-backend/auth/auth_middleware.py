from starlette.authentication import AuthenticationError, BaseUser
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from firebase_admin import auth
from models import user as usermodel

from db.database import get_db, SessionLocal
from routers.users import create_user
from schemas.user_schema import UserCreate

CREDENTIALS_TYPE = 'Bearer'
CREDENTIALS_HEADER_NAME = 'Authorization'


class AuthMiddleware(BaseHTTPMiddleware):
    default_error_message = 'unauthorized'

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == 'OPTIONS':
            return await call_next(request)

        try:
            if 'login' in str(request.url):
                user_email, user_id = self.authenticate_token(request, True)
            else:
                user_email, user_id = self.authenticate_token(request)
        except AuthenticationError:
            return self.on_error()

        request.state.user_email = user_email
        request.state.user_id = user_id
        return await call_next(request)

    def authenticate_token(self, request: Request, register_if_not_exists: bool = False):
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
        user_name = firebase_token.get('name')

        db = SessionLocal()

        user = db.query(usermodel.User).filter(usermodel.User.email == user_email).first()
        if not user:
            if not register_if_not_exists:
                db.close()
                raise AuthenticationError(self.default_error_message)
            else:
                print(f"Creating user {user_email} with name {user_name}")
                user = create_user(db, UserCreate(name=user_name, email=user_email))

        db.close()
        return user_email, user.id

    def on_error(self):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
