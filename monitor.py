from utils import fetch_html, normalize_html, hash_text, make_diff
import logging

logger = logging.getLogger(__name__)

class Monitor:
    def __init__(self):
        self.monitored_sites = {}

    def add_site(self, url: str) -> None:
        if url not in self.monitored_sites:
            self.monitored_sites[url] = {"hash": None, "text": ""}
            logger.info(f"Добавлен сайт для мониторинга: {url}")

    def remove_site(self, url: str) -> None:
        if url in self.monitored_sites:
            del self.monitored_sites[url]
            logger.info(f"Удален сайт из мониторинга: {url}")

    def check_changes(self, url: str) -> dict:
        if url not in self.monitored_sites:
            return {"error": f"Сайт {url} не находится в мониторинге"}

        old_hash = self.monitored_sites[url]["hash"]
        old_text = self.monitored_sites[url]["text"]

        try:
            html = fetch_html(url)
        except Exception as e:
            logger.error(f"Ошибка загрузки {url}: {e}")
            return {"error": f"Ошибка загрузки: {e}"}

        new_text = normalize_html(html)
        new_hash = hash_text(new_text)

        # Если это первая проверка (old_hash == None), сохраняем состояние без уведомления
        if old_hash is None:
            self.monitored_sites[url] = {"hash": new_hash, "text": new_text}
            return {"changed": False, "initialized": True}

        if new_hash != old_hash:
            diff = make_diff(old_text, new_text)
            self.monitored_sites[url] = {"hash": new_hash, "text": new_text}
            return {"changed": True, "diff": diff, "url": url}
        else:
            return {"changed": False}

    def get_monitored_sites(self) -> list:
        return list(self.monitored_sites.keys())