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

    async def get_recipe_suggestions(self, prompt: str) -> str:
        with self.client as giga:
            full_prompt = (
                f"Ты шеф-повар. Предложи рецепт по запросу: {prompt}. "
                "ВАЖНО: Используй только стандартную разметку Markdown. "
                "Для заголовков используй жирный текст (например, **Ингредиенты:**). "
                "Не используй символы # или ###."
            )
            response = giga.chat(full_prompt)
            return response.choices[0].message.content
