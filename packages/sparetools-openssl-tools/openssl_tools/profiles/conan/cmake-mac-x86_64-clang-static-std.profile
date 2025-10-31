include(default)

[settings]
os=Macos
os.version=14.0
arch=x86_64
compiler=apple-clang
compiler.version=15
compiler.libcxx=libc++
compiler.cppstd=gnu17
build_type=Release

[options]
sparetools-openssl/*:shared=False
sparetools-openssl/*:enable_fips=False
sparetools-openssl/*:no_apps=True

[conf]
tools.build:jobs=8
tools.build:cflags=["-O3"]
tools.build:cxxflags=["-O3"]
user.sparetools.openssl:variant=cmake
user.sparetools.openssl:linkage=static
user.sparetools.openssl:fips=off
user.sparetools.openssl:target=darwin64-x86_64-cc
user.sparetools.openssl:openssl_release=v3_6_0
user.sparetools.openssl:optimization_tier=opt-speed
user.sparetools.openssl:profile_id=cmake-mac-x86_64-clang-static-std
