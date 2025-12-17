from sparetools_recipe_base import SpareToolsConsumerBase


class SparetoolsOBDSimConan(SpareToolsConsumerBase):
    name = "sparetools-obd-sim"
    version = "2.0.0"
    description = "OBD-II simulation tooling packaged for SpareTools and MIA"

    python_requires = "sparetools-base/2.0.0", "sparetools-recipe-base/1.0.0"
    tool_requires = "sparetools-cpython/3.12.7"

    exports_sources = "sparetools_obd/**"
