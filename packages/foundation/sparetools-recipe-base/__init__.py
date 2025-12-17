"""
SpareTools Recipe Base Classes

This package provides base classes for the SpareTools layered architecture:
- SpareToolsFoundationBase: For foundation packages that provide core utilities
- SpareToolsConsumerBase: For consumer packages that are end-user applications

Usage:
    from sparetools_recipe_base import SpareToolsFoundationBase, SpareToolsConsumerBase

    class MyFoundationPackage(SpareToolsFoundationBase):
        name = "my-package"
        version = "1.0.0"
        # ... package-specific attributes
"""

from .conanfile import SpareToolsFoundationBase, SpareToolsConsumerBase

__all__ = ["SpareToolsFoundationBase", "SpareToolsConsumerBase"]