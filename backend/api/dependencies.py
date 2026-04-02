from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import List, Dict

from backend.infrastructure.auth import decode_access_token
from backend.domain.enums import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise credentials_exception

def require_role(allowed_roles: List[Role]):
    def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user.get("role") not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta operacion"
            )
        return current_user
    return role_checker

require_admin = require_role([Role.ADMIN])
require_supervisor = require_role([Role.ADMIN, Role.SUPERVISOR])