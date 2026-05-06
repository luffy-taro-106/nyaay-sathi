import app.services.chat_store as chat_store
import pytest


@pytest.fixture(autouse=True)
def isolated_chat_sqlite(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Avoid polluting repo chat.sqlite during tests."""
    monkeypatch.setattr(chat_store, "_DB_PATH", tmp_path / "chat_test.sqlite")
