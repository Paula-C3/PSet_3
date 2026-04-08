from fastapi import Depends, HTTPException, status  #type:ignore
from fastapi.security import OAuth2PasswordBearer   #type:ignore
from sqlalchemy.orm import Session                  #type:ignore
from jose import JWTError                           #type:ignore
from typing import List, Dict

from backend.infrastructure.auth import decode_access_token
from backend.domain.enums import Role
from backend.infrastructure.database import get_db
from backend.infrastructure.repositories import SQLAlchemyUserRepository
from backend.domain.entities import User



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("user_id") or ""
        if user_id is None:
            raise credentials_exception
        repo = SQLAlchemyUserRepository(db)
        user = repo.find_by_id(user_id)
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def require_role(allowed_roles: List[Role]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta operacion"
            )
        return current_user
    return role_checker

require_admin = require_role([Role.ADMIN])
require_supervisor = require_role([Role.ADMIN, Role.SUPERVISOR])