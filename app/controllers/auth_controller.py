from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

from app.core.dependencies import get_user_service, get_auth_service
from app.schemas.user import UserResponse, UserCreate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user_data)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                auth_service: AuthService = Depends(get_auth_service)):
    user_with_token = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user_with_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user_with_token
