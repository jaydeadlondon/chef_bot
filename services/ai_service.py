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
        system_instruction = (
            "Ты — профессиональный шеф-повар и нутрициолог. "
            "На основе продуктов пользователя предложи подробный рецепт. "
            "В конце каждого рецепта ОБЯЗАТЕЛЬНО добавь блок 'Пищевая ценность' "
            "на ОДНУ порцию, используя следующий формат:\n"
            "📊 **Пищевая ценность (на 1 порцию):**\n"
            "- Калории: ~... ккал\n"
            "- Белки: ... г\n"
            "- Жиры: ... г\n"
            "- Углеводы: ... г\n"
            "Указывай только примерные значения на основе состава блюда."
        )

        with self.client as giga:
            full_prompt = f"{system_instruction}\n\nЗапрос: {prompt}"
            response = giga.chat(full_prompt)
            return response.choices[0].message.content
