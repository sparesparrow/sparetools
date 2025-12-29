"""
SpareTools Aerospace Package

This package contains aerospace-specific implementations of environments,
components, and verifiers for the SpareTools framework.
"""

from .environments.ase_environment import ASEEnvironment
from .environments.jets_environment import JETSEnvironment
from .environments.sits_environment import SITSEnvironment
from .components.ase_component import ASEComponent
from .components.deos_component import DEOSComponent
from .components.jets_component import JETSComponent


def register_aerospace_plugins(plugin_manager):
    """
    Register all aerospace-specific plugins with the plugin manager.

    Args:
        plugin_manager: The SpareTools plugin manager instance
    """
    # Register environments
    plugin_manager.register_environment("ase", ASEEnvironment)
    plugin_manager.register_environment("jets", JETSEnvironment)
    plugin_manager.register_environment("sits", SITSEnvironment)

    # Register components
    plugin_manager.register_component("ase", ASEComponent)
    plugin_manager.register_component("deos", DEOSComponent)
    plugin_manager.register_component("jets", JETSComponent)

    # Note: Verifiers would be registered here if they existed
    # plugin_manager.register_verifier("aerospace_verifier", AerospaceVerifier)