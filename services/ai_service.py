from abc import ABC, abstractmethod
from gigachat import GigaChat
from core.config import config


class AIService(ABC):
    @abstractmethod
    async def get_recipe_suggestions(self, ingredients: str) -> str:
        pass


class GigaChatService(AIService):
    def __init__(self):
        self.client = GigaChat(
            credentials=config.gigachat_credentials.get_secret_value(),
            verify_ssl_certs=False,
        )

    async def get_recipe_suggestions(self, ingredients: str) -> str:
        system_prompt = (
            "Ты — профессиональный шеф-повар. Твоя задача — предложить рецепты "
            "на основе списка продуктов от пользователя. Отвечай структурировано."
        )

        with self.client as giga:
            response = giga.chat(f"{system_prompt}\nПродукты: {ingredients}")
            return response.choices[0].message.content
