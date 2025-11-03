#!/bin/bash
set -e

echo "🚀 Setting up OpenSSL Development Environment"
echo "============================================"

# Load environment variables
if [ -f ../.env ]; then
    source ../.env
fi

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 required"; exit 1; }
command -v conan >/dev/null 2>&1 || { echo "❌ Conan required"; exit 1; }
command -v cmake >/dev/null 2>&1 || { echo "❌ CMake required"; exit 1; }
echo "✅ Prerequisites OK"

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
cd mcp-project-orchestrator
python3 -m venv venv
source venv/bin/activate
pip install -e .
cd ..

echo "📦 Configuring Conan..."
# Configure Conan remote
conan remote add ${CONAN_REPOSITORY_NAME} \
    ${CONAN_REPOSITORY_URL} \
    --force

# Authenticate if API key provided
if [ -n "$CLOUDSMITH_API_KEY" ] && [ "$CLOUDSMITH_API_KEY" != "your-api-key-here" ]; then
    echo "🔐 Authenticating with Cloudsmith..."
    conan remote login ${CONAN_REPOSITORY_NAME} spare-sparrow --password "$CLOUDSMITH_API_KEY"
else
    echo "⚠️  CLOUDSMITH_API_KEY not set - some tests will be skipped"
fi

# Initialize Conan profile
conan profile detect

echo "🧪 Setting up test environment..."
# Create test results directory
mkdir -p test-results
mkdir -p performance-logs

echo "🤖 Setting up AI integration..."
# Deploy Cursor configuration
cd mcp-project-orchestrator
source venv/bin/activate
mcp-orchestrator deploy-cursor --project-type openssl --force || echo "⚠️  Cursor deployment failed - will work when IDE is open"
cd ..

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Set CLOUDSMITH_API_KEY in .env file"
echo "  2. Run: ./scripts/run-integration-tests.sh"
echo "  3. Open workspace in Cursor IDE"
echo "  4. Start MCP server: cd mcp-project-orchestrator && source venv/bin/activate && python -m mcp_project_orchestrator"
