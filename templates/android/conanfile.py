from conan import ConanFile

class {{class_name}}Android(ConanFile):
    name = "{{project_name}}"
    version = "{{version}}"
    description = "{{project_description}}"
    license = "{{license}}"
    author = "{{author}}"
    url = "{{repository_url}}"
    topics = ("android", "mobile", "openssl", "sparetools")

    # Use SpareTools base utilities
    python_requires = "sparetools-base/{{base_version}}"

    # Tool requirements - hermetic Python environment for build scripts
    tool_requires = (
        "sparetools-cpython/{{cpython_version}}",
    )

    # Settings for Android development
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        # This project delegates native dependencies to the app module
        # Add any additional Android-specific requirements here
        pass