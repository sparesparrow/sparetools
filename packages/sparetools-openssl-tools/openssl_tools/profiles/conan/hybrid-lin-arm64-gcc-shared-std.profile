include(default)

[settings]
os=Linux
arch=armv8
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
compiler.cppstd=gnu17
build_type=Release

[options]
sparetools-openssl/*:shared=True
sparetools-openssl/*:enable_fips=False
sparetools-openssl/*:no_apps=False

[conf]
tools.build:jobs=8
user.sparetools.openssl:variant=hybrid
user.sparetools.openssl:linkage=shared
user.sparetools.openssl:fips=off
user.sparetools.openssl:target=linux-aarch64
user.sparetools.openssl:openssl_release=v3_3_2
user.sparetools.openssl:optimization_tier=opt-balanced
user.sparetools.openssl:profile_id=hybrid-lin-arm64-gcc-shared-std
