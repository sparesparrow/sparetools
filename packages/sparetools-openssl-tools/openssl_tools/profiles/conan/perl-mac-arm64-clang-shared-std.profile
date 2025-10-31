include(default)

[settings]
os=Macos
os.version=14.0
arch=armv8
compiler=apple-clang
compiler.version=15
compiler.libcxx=libc++
compiler.cppstd=gnu17
build_type=Release

[options]
sparetools-openssl/*:shared=True
sparetools-openssl/*:enable_fips=False
sparetools-openssl/*:no_apps=False

[conf]
tools.build:jobs=8
user.sparetools.openssl:variant=perl-configure
user.sparetools.openssl:linkage=shared
user.sparetools.openssl:fips=off
user.sparetools.openssl:target=darwin64-arm64-cc
user.sparetools.openssl:openssl_release=v3_3_2
user.sparetools.openssl:optimization_tier=opt-balanced
user.sparetools.openssl:profile_id=perl-mac-arm64-clang-shared-std
