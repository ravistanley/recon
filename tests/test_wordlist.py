import pytest
from pathlib import Path
from config.wordlist_registry import WordlistRegistry
from core.wordlist_selector import detect_task_type, get_wordlist_for_task
from models.service import ServiceCategory, ServiceIdentity

class TestWordlistRegistry:
    def test_registry_scan_and_categorize(self, tmp_path):
        # Create fake wordlist files
        dir_list = tmp_path / "common.txt"
        dir_list.write_text("admin\nlogin")
        vhost_list = tmp_path / "subdomains.txt"
        vhost_list.write_text("www\nmail")
        fallback_list = tmp_path / "rockyou.txt"
        fallback_list.write_text("password")

        # Monkeypatch WORDLIST_ROOTS
        import config.wordlist_registry
        original_roots = config.wordlist_registry.WORDLIST_ROOTS
        config.wordlist_registry.WORDLIST_ROOTS = [str(tmp_path)]

        registry = WordlistRegistry()
        assert registry.get_best("dir") == str(dir_list)
        assert registry.get_best("vhost") == str(vhost_list)
        # fallback: largest file among all (rockyou likely larger)
        assert registry.get_best("nonexistent") in [str(fallback_list), str(dir_list), str(vhost_list)]

        config.wordlist_registry.WORDLIST_ROOTS = original_roots

    def test_registry_cache(self, tmp_path):
        import config.wordlist_registry
        original_roots = config.wordlist_registry.WORDLIST_ROOTS
        config.wordlist_registry.WORDLIST_ROOTS = [str(tmp_path)]
        cache_file = config.wordlist_registry.CACHE_DIR / "wordlist_index.json"
        if cache_file.exists():
            cache_file.unlink()

        registry = WordlistRegistry()
        assert cache_file.exists()

        config.wordlist_registry.WORDLIST_ROOTS = original_roots

@pytest.mark.asyncio
class TestWordlistSelector:
    async def test_detect_task_type_http(self):
        svc = ServiceIdentity(port=80, category=ServiceCategory.HTTP, product="nginx", version="1.18", cpe=None)
        task = await detect_task_type("example.com", 80, False, svc.category)
        assert task == "dir"

    async def test_detect_task_type_https(self):
        svc = ServiceIdentity(port=443, category=ServiceCategory.HTTPS, product="Apache", version="2.4", cpe=None)
        task = await detect_task_type("example.com", 443, True, svc.category)
        assert task == "dir"

    async def test_get_wordlist_for_task_returns_none_if_not_found(self):
        # Temporarily empty registry
        import config.wordlist_registry
        original_registry = config.wordlist_registry.registry
        config.wordlist_registry.registry = WordlistRegistry()
        config.wordlist_registry.registry.lists = {}
        wordlist = await get_wordlist_for_task("dir")
        assert wordlist is None
        config.wordlist_registry.registry = original_registry