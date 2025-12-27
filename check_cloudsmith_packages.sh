#!/bin/bash

echo "=== Cloudsmith Package Repository Check ==="
echo "Repository: https://cloudsmith.io/~sparesparrow-conan/packages/"
echo ""

echo "🔍 Checking Docker Conan environment..."
if [ -f "scripts/run-conan-docker.sh" ]; then
    echo "✅ Docker Conan script found"
else
    echo "❌ Docker Conan script not found"
    exit 1
fi

echo ""
echo "📦 Available Package Categories in sparetools:"
ls packages/ | while read category; do
    package_count=$(find "packages/$category" -name "conanfile.py" 2>/dev/null | wc -l)
    echo "  • $category: $package_count packages"
done

echo ""
echo "🚀 Publishing Commands:"
echo ""
echo "# 1. Authenticate with Cloudsmith:"
echo "export CLOUDSMITH_API_KEY=your_api_key_here"
echo "./scripts/run-conan-docker.sh remote login sparesparrow-conan spare-sparrow --password \"\$CLOUDSMITH_API_KEY\""
echo ""
echo "# 2. Upload all sparetools packages:"
echo "./scripts/run-conan-docker.sh upload \"sparetools-*/*\" -r sparesparrow-conan --confirm"
echo ""
echo "# 3. Or upload specific packages:"
echo "./scripts/run-conan-docker.sh upload \"sparetools-base/2.0.3\" -r sparesparrow-conan --confirm"
echo ""
echo "# 4. List published packages:"
echo "./scripts/run-conan-docker.sh list \"sparetools-*\" -r sparesparrow-conan"
echo ""
echo "# 5. Search for packages:"
echo "./scripts/run-conan-docker.sh search \"sparetools-*\" -r sparesparrow-conan"

echo ""
echo "📋 Package Categories Available:"
echo "• foundation/ - Core libraries and utilities"
echo "• consumers/ - Consumer-specific packages (MIA, ESP32, Android, MCP)"
echo "• input/ - Input handling and gamepad support"
echo "• streaming/ - RTSP/HLS streaming solutions"
echo "• wifi/ - WiFi sensing and CSI processing"
echo "• pentest/ - Penetration testing tools"
echo "• prompt/ - Prompt system and web interfaces"
echo "• sdr/ - SDR and RF analysis tools"
echo "• security/ - Security and cryptography packages"
echo "• embedded/ - Embedded systems packages"
echo "• devops/ - DevOps and CI/CD tools"
echo "• python/ - Python-specific packages"

echo ""
echo "🎯 Next Steps:"
echo "1. Set your CLOUDSMITH_API_KEY environment variable"
echo "2. Run the authentication command"
echo "3. Publish packages using the upload commands above"
echo "4. Verify packages are available at: https://cloudsmith.io/~sparesparrow-conan/packages/"
