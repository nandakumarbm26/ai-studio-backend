from typing import Type, TypeVar, Callable, cast
from functools import wraps
from strawberry.types import Info
from fastapi import HTTPException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.crud import auth as cruds
from app.schemas.auth import UserOut

T = TypeVar("T")

def requires_auth(resolver: Callable[..., T]) -> Callable[..., T]:
    @wraps(resolver)
    def wrapper(self, info: Info, **kwargs) -> T:
        request = info.context["request"]
        token = request.cookies.get("access_token")
        if not token:
            raise Exception("Not authenticated")
        
        auth_header = dict(request.headers).get("authorization")

        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        try:
            token = auth_header.split("Bearer ")[1]
        except IndexError:
            raise HTTPException(status_code=401, detail="Invalid Authorization format")

        payload = decode_access_token(token)
        
        if not payload or "sub" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        email = payload["sub"]
        db = next(get_db())
        user = cruds.get_user_by_email(db, email)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        info.context["user"] = UserOut(**user.__dict__)
        return resolver(self, info, **kwargs)

    return cast(Callable[..., T], wrapper)


T = TypeVar('T')
S = TypeVar('S')

def map_model(source: S, target_class: Type[T]) -> T:
    """
    General utility to map a source model to a target model,
    assuming overlapping field names.
    """
    source_dict = source.__dict__ if hasattr(source, '__dict__') else dict(source)
    target_fields = target_class.__annotations__.keys()
    filtered_data = {field: source_dict[field] for field in target_fields if field in source_dict}
    return target_class(**filtered_data)

