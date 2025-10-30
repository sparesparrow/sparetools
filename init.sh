# Step 1: Clone your empty sparetools repo
cd ~
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools

# Step 2: Create directory structure
mkdir -p packages/sparetools-base
mkdir -p packages/sparetools-cpython
mkdir -p docs
mkdir -p scripts

# Step 3: Copy sparetools-base files
cp ~/.openssl-bootstrap/cpy-tools/conanfile.py packages/sparetools-base/
cp ~/.openssl-bootstrap/cpy-tools/symlink_helpers.py packages/sparetools-base/
cp ~/.openssl-bootstrap/cpy-tools/security_gates.py packages/sparetools-base/
cp ~/.openssl-bootstrap/cpy-tools/__init__.py packages/sparetools-base/ 2>/dev/null || true

# Update package name in sparetools-base
sed -i 's/name = "cpy-tools"/name = "sparetools-base"/' packages/sparetools-base/conanfile.py

# Step 4: Copy sparetools-cpython files
cp ~/.openssl-bootstrap/cpy/conanfile.py packages/sparetools-cpython/

# Update package name and URL in sparetools-cpython
sed -i 's/name = "cpython-tool"/name = "sparetools-cpython"/' packages/sparetools-cpython/conanfile.py
sed -i 's|url = "https://github.com/sparesparrow/cpy"|url = "https://github.com/sparesparrow/sparetools"|' packages/sparetools-cpython/conanfile.py



