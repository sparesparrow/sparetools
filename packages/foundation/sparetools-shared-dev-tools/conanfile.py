from sparetools_recipe_base import SpareToolsFoundationBase

class SpareToolsSharedDevToolsConan(SpareToolsFoundationBase):
    name = "sparetools-shared-dev-tools"
    version = "2.0.0"
    description = "Shared development tools for SpareTools ecosystem"

    exports_sources = "shared_dev_tools/**", "scripts/**"

    python_requires = "sparetools-base/2.0.0", "sparetools-recipe-base/1.0.0"
