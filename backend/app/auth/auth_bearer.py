from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_handler import decodeJWT


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            user_id = self.verify_jwt(credentials.credentials)

            if not user_id:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")

            return user_id
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        is_token_valid: bool = False
        user_id = None

        try:
            payload = decodeJWT(jwtoken)
            user_id = payload.get("user_id")
            is_token_valid = True
        except:
            pass
        return user_id if is_token_valid else False