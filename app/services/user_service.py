from fastapi import HTTPException
from starlette import status
from app.respositories.user_respositories import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.auth_service = AuthService(user_repository)

    async def create_user(self, user_data: UserCreate):
        user_name = await self.user_repository.get_by_username(user_data.username)
        if user_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_RQUEST,
                detail="Username already registered"
            )
        user_email = await self.user_repository.get_by_email(user_data.email)
        if user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        try:
            user_dict = user_data.model_dump()
            user_dict["hashed_password"] = self.auth_service.get_password_hash(user_data.password)
            del user_dict["password"]

            user = await self.user_repository.create(user_dict)
            return UserResponse.model_validate(user)
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )



