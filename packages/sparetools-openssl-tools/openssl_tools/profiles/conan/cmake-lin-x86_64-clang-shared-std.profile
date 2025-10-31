include(default)

[settings]
os=Linux
arch=x86_64
compiler=clang
compiler.version=15
compiler.libcxx=libstdc++11
compiler.cppstd=gnu17
build_type=Release

[options]
sparetools-openssl/*:shared=True
sparetools-openssl/*:enable_fips=False
sparetools-openssl/*:no_apps=False

[conf]
tools.build:jobs=8
tools.build:cflags=["-O3"]
tools.build:cxxflags=["-O3"]
user.sparetools.openssl:variant=cmake
user.sparetools.openssl:linkage=shared
user.sparetools.openssl:fips=off
user.sparetools.openssl:target=linux-x86_64
user.sparetools.openssl:openssl_release=v3_6_0
user.sparetools.openssl:optimization_tier=opt-speed
user.sparetools.openssl:profile_id=cmake-lin-x86_64-clang-shared-std
