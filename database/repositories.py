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

    async def update_preferences(self, tg_id: int, preferences: str):
        user = await self.get_or_create_user(tg_id, None)
        user.preferences = preferences
        await self.session.commit()

    async def get_user(self, tg_id: int) -> User:
        query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(query)
        return result.scalar_one()


class RecipeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_recipe(self, tg_id: int, title: str, content: str):
        user_query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(user_query)
        user = result.scalar_one()

        new_recipe = FavoriteRecipe(user_id=user.id, title=title, content=content)
        self.session.add(new_recipe)
        await self.session.commit()

    async def get_user_recipes(self, tg_id: int):
        query = (
            select(FavoriteRecipe)
            .join(User)
            .where(User.tg_id == tg_id)
            .order_by(FavoriteRecipe.id.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_recipe_by_id(self, recipe_id: int):
        query = select(FavoriteRecipe).where(FavoriteRecipe.id == recipe_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_recipe(self, recipe_id: int):
        from sqlalchemy import delete

        query = delete(FavoriteRecipe).where(FavoriteRecipe.id == recipe_id)
        await self.session.execute(query)
        await self.session.commit()
