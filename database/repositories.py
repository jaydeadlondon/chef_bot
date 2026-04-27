from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, FavoriteRecipe


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, tg_id: int, username: str | None) -> User:
        query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            user = User(tg_id=tg_id, username=username)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user


class RecipeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_favorite(self, user_id: int, title: str, content: str):
        recipe = FavoriteRecipe(user_id=user_id, title=title, content=content)
        self.session.add(recipe)
        await self.session.commit()
