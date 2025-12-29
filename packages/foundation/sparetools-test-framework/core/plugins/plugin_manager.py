"""
Simple plugin manager using proven patterns from existing codebase.
References: ngapy/conan/conan_functions.py for package loading patterns.
"""

import importlib
from typing import Dict, Type, Any


class PluginManager:
    def __init__(self):
        self._environments: Dict[str, Type] = {}
        self._components: Dict[str, Type] = {}
        self._verifiers: Dict[str, Type] = {}

    def register_environment(self, name: str, env_class: Type):
        self._environments[name] = env_class

    def register_component(self, name: str, comp_class: Type):
        self._components[name] = comp_class

    def register_verifier(self, name: str, ver_class: Type):
        self._verifiers[name] = ver_class

    def load_plugin(self, module_name: str):
        """Load plugin using standard importlib"""
        try:
            module = importlib.import_module(module_name)
            # Auto-discover plugin classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, 'register_plugin'):
                    attr.register_plugin(self)
        except ImportError as e:
            raise PluginLoadError(f"Failed to load plugin {module_name}: {e}")

    def get_environment(self, name: str) -> Type:
        return self._environments.get(name)

    def get_component(self, name: str) -> Type:
        return self._components.get(name)

    def get_verifier(self, name: str) -> Type:
        return self._verifiers.get(name)

    def list_environments(self) -> list:
        return list(self._environments.keys())

    def list_components(self) -> list:
        return list(self._components.keys())

    def list_verifiers(self) -> list:
        return list(self._verifiers.keys())


class PluginLoadError(Exception):
    """Exception raised when plugin loading fails"""
    pass