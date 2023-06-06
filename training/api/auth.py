
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from training.config import settings


class JWTUser(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            user = self.decode_jwt(credentials.credentials)
            if user is None:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return user
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def decode_jwt(self, token: str):
        try:
            return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except jwt.exceptions.InvalidTokenError:
            return


class RequireRole:
    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = set(required_roles)

    def __call__(self, user=Depends(JWTUser())):
        try:
            user_roles = user['roles']
        except KeyError:
            raise HTTPException(status_code=401, detail="Not Authorized")

        if all(role in user_roles for role in self.required_roles):
            return user
        else:
            print("**** here ****")
            raise HTTPException(status_code=401, detail="Not Authorized")
