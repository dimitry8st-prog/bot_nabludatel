import hashlib
import requests
from difflib import unified_diff
import logging

logger = logging.getLogger(__name__)

def fetch_html(url: str, timeout: int = 30) -> str:
    """
    Загружает HTML содержимое страницы.
    
    Args:
        url: URL страницы для загрузки
        timeout: Таймаут запроса в секундах
        
    Returns:
        HTML содержимое страницы
        
    Raises:
        requests.RequestException: При ошибке загрузки
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.Timeout:
        logger.error(f"Таймаут при загрузке {url}")
        raise
    except requests.RequestException as e:
        logger.error(f"Ошибка при загрузке {url}: {e}")
        raise

def normalize_html(html: str) -> str:
    """
    Нормализует HTML, удаляя лишние пробелы.
    
    Args:
        html: Исходный HTML
        
    Returns:
        Нормализованный текст
    """
    return " ".join(html.split())

def hash_text(text: str) -> str:
    """
    Вычисляет MD5 хеш текста.
    
    Args:
        text: Текст для хеширования
        
    Returns:
        MD5 хеш в виде hex строки
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def make_diff(old_text: str, new_text: str) -> list:
    """
    Создает diff между двумя текстами.
    
    Args:
        old_text: Старый текст
        new_text: Новый текст
        
    Returns:
        Список строк diff
    """
    return list(unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        lineterm=''
    ))