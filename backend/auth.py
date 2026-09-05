import hashlib
import hmac
import os
from urllib.parse import parse_qsl
from dotenv import load_dotenv
 
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
 
 
def validate_init_data(init_data: str) -> dict | None:
    """
    Telegram Mini App при открытии присылает строку initData,
    подписанную секретным ключом на основе токена бота.
    Мы пересчитываем подпись сами и сверяем - совпало = запрос настоящий.
    """
    try:
        parsed = dict(parse_qsl(init_data))
        received_hash = parsed.pop("hash", None)
 
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )
 
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
 
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
 
        if calculated_hash != received_hash:
            return None
 
        return parsed
    except Exception:
        return None
