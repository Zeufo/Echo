import builtins
import random
import uuid

import requests
from locust import HttpUser, between, events, task
from loguru import logger

# Глобальный список с реальными UUID постов
PRESEEDED_POST_IDS: list[str] = []

print = logger.debug


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    При старте теста запрашиваем реальные посты у запущенного API через HTTP.
    Это исключает конфликты asyncio с Gevent внутри Locust.
    """
    global PRESEEDED_POST_IDS
    host = environment.host or "http://127.0.0.1:8000"
    url = f"{host.rstrip('/')}/api/v1/feed/top"
    try:
        print(f"🔄 [Locust] Загрузка постов через {url}...")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            posts = response.json()
            if isinstance(posts, list) and len(posts) > 0:
                PRESEEDED_POST_IDS = [
                    p["id"] for p in posts if isinstance(p, dict) and "id" in p
                ]
                print(
                    f"✅ [Locust] Успешно загружено {len(PRESEEDED_POST_IDS)} ID постов из API."
                )
            else:
                print("⚠️ [Locust] Запрос вернул пустой список постов.")
        else:
            print(f"⚠️ [Locust] API вернул статус {response.status_code}.")
    except Exception as e:
        print(f"❌ [Locust] Не удалось подключиться к API: {e}")


class HighLoadUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def _get_target_post_id(self) -> str:
        """Берет реальный UUID поста или генерирует новый, если список пуст"""
        if PRESEEDED_POST_IDS:
            return random.choice(PRESEEDED_POST_IDS)
        return str(uuid.uuid4())

    # 70
    @task(0)
    def get_post(self):
        """
        70% нагрузки: Чтение поста по ID.
        """
        post_id = self._get_target_post_id()
        self.client.get(f"/api/v1/posts/{post_id}", name="/api/v1/posts/[id]")

    # 15
    @task(100)
    def give_like(self):
        """
        15% нагрузки: Постановка лайка на пост.
        """
        post_id = self._get_target_post_id()
        user_id = random.randint(1, 10_000_000)
        self.client.post(
            f"/api/v1/posts/{post_id}/like?user_id={user_id}",
            name="/api/v1/posts/[id]/like",
        )

    # 10
    @task(0)
    def get_feed_top(self):
        """
        10% нагрузки: Запрос топа популярных постов.
        """
        self.client.get("/api/v1/feed/top", name="/api/v1/feed/top")

    # 5
    @task(0)
    def create_post(self):
        """
        5% нагрузки: Создание нового поста и сохранение его ID.
        """
        text = f"Locust post {random.randint(1000, 9999)}"
        response = self.client.post(
            f"/api/v1/posts/?text={text}", name="/api/v1/posts/"
        )
        if response.status_code == 200:
            try:
                data = response.json()
                new_id = data.get("id") if isinstance(data, dict) else None
                if new_id:
                    PRESEEDED_POST_IDS.append(new_id)
            except Exception:
                pass
