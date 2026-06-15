import importlib
import pkgutil
from plugins.base import ReconPlugin

class PluginManager:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugins = {}
        self._load_plugins(plugin_dir)

    def _load_plugins(self, plugin_dir):
        for module_info in pkgutil.iter_modules([plugin_dir]):
            if module_info.name in ("base", "manager"):
                continue
            module = importlib.import_module(f"{plugin_dir}.{module_info.name}")
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, ReconPlugin) and obj != ReconPlugin:
                    inst = obj()
                    self.plugins[inst.name] = inst

    def resolve_dependencies(self):
        order = []
        remaining = set(self.plugins.keys())
        while remaining:
            progress = False
            for name in list(remaining):
                deps = self.plugins[name].dependencies
                if all(d in order for d in deps):
                    order.append(name)
                    remaining.remove(name)
                    progress = True
            if not progress:
                order.extend(remaining)
                break
        self.execution_order = order

    async def execute_plugins(self, target: str, scan_data: dict, session):
        results = {}
        for name in self.execution_order:
            plugin = self.plugins[name]
            try:
                results[name] = await plugin.run(target, scan_data, session)
            except Exception as e:
                print(f"[!] Plugin '{name}' failed: {e}")
                results[name] = {"error": str(e)}
        return results