import pytest
import importlib
from pathlib import Path
from models.service import ServiceCategory, ServiceIdentity

class TestWordlistRegistry:
    def test_registry_scan_and_categorize(self, tmp_path):
        # Create fake wordlist files
        dir_list = tmp_path / "common.txt"
        dir_list.write_text("admin\nlogin")
        (tmp_path / "subdomains.txt").write_text("www\nmail")
        (tmp_path / "rockyou.txt").write_text("password")
        huge_file = tmp_path / "huge.txt"
        huge_file.write_text("x" * 10_000_000)

        # Save original WORDLIST_ROOTS
        import config.settings
        original_roots = config.settings.WORDLIST_ROOTS
        config.settings.WORDLIST_ROOTS = [str(tmp_path)]

        # Reload wordlist_registry to pick up new setting
        import config.wordlist_registry
        importlib.reload(config.wordlist_registry)
        from config.wordlist_registry import WordlistRegistry

        # Clear cache
        from config.settings import CACHE_DIR
        cache_file = CACHE_DIR / "wordlist_index.json"
        if cache_file.exists():
            cache_file.unlink()

        try:
            registry = WordlistRegistry()
            best_dir = registry.get_best("dir")
            # Should be common.txt (contains 'common')
            assert best_dir == str(dir_list)
        finally:
            # Restore original roots and reload
            config.settings.WORDLIST_ROOTS = original_roots
            importlib.reload(config.wordlist_registry)

    def test_registry_cache(self, tmp_path):
        import config.settings
        original_roots = config.settings.WORDLIST_ROOTS
        config.settings.WORDLIST_ROOTS = [str(tmp_path)]
        import config.wordlist_registry
        importlib.reload(config.wordlist_registry)
        from config.wordlist_registry import WordlistRegistry
        from config.settings import CACHE_DIR
        cache_file = CACHE_DIR / "wordlist_index.json"
        if cache_file.exists():
            cache_file.unlink()
        try:
            registry = WordlistRegistry()
            assert cache_file.exists()
        finally:
            config.settings.WORDLIST_ROOTS = original_roots
            importlib.reload(config.wordlist_registry)

@pytest.mark.asyncio
class TestWordlistSelector:
    async def test_detect_task_type_http(self):
        svc = ServiceIdentity(port=80, category=ServiceCategory.HTTP, product="nginx", version="1.18", cpe=None)
        from core.wordlist_selector import detect_task_type
        task = await detect_task_type("example.com", 80, False, svc.category)
        assert task == "dir"

    async def test_detect_task_type_https(self):
        svc = ServiceIdentity(port=443, category=ServiceCategory.HTTPS, product="Apache", version="2.4", cpe=None)
        from core.wordlist_selector import detect_task_type
        task = await detect_task_type("example.com", 443, True, svc.category)
        assert task == "dir"

    async def test_get_wordlist_for_task_returns_none_if_not_found(self):
        import core.wordlist_selector as wsel
        original_registry = wsel.registry
        from config.wordlist_registry import WordlistRegistry
        empty_registry = WordlistRegistry()
        empty_registry.lists = {}
        wsel.registry = empty_registry
        try:
            from core.wordlist_selector import get_wordlist_for_task
            wordlist = await get_wordlist_for_task("dir")
            assert wordlist is None
        finally:
            wsel.registry = original_registry