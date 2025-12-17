from conan import ConanFile
from conan.tools.python import PythonDeps
import os
import subprocess
import sys


class {{class_name}}McpServerTestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        self.folders.generators = "conan"

    def generate(self):
        py_deps = PythonDeps(self)
        py_deps.generate()

    def test(self):
        # Import and test the package
        import sys
        sys.path.insert(0, self.dependencies[self.tested_reference_str].cpp_info.libdirs[0])

        try:
            from {{module_name}} import {{class_name}}Server, __version__

            # Test basic functionality
            server = {{class_name}}Server()
            assert server.tools is not None
            assert server.resources is not None

            assert __version__ == "{{version}}"

            self.output.info("✅ Basic import tests passed!")

            # Test tool execution (synchronous for simplicity in test package)
            import asyncio

            async def test_tools():
                tools = await server.server.list_tools()()
                assert len(tools) > 0

                # Test example tool
                from mcp.types import CallToolRequest
                request = CallToolRequest(
                    method="tools/call",
                    params={
                        "name": "example_tool",
                        "arguments": {"input": "test"}
                    }
                )
                results = await server.server.call_tool()(request)
                assert len(results) > 0

                return True

            # Run async test
            result = asyncio.run(test_tools())
            assert result

            self.output.info("✅ Tool execution tests passed!")

        except ImportError as e:
            self.output.error(f"❌ Import failed: {e}")
            raise
        except Exception as e:
            self.output.error(f"❌ Test failed: {e}")
            raise