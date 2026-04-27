from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, FavoriteRecipe


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
