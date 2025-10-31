include(default)

[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
compiler.cppstd=gnu17
build_type=Release

[options]
sparetools-openssl/*:shared=False
sparetools-openssl/*:enable_fips=False
sparetools-openssl/*:no_apps=True

[conf]
tools.build:jobs=8
user.sparetools.openssl:variant=autotools
user.sparetools.openssl:linkage=static
user.sparetools.openssl:fips=off
user.sparetools.openssl:target=linux-x86_64
user.sparetools.openssl:openssl_release=v3_3_2
user.sparetools.openssl:optimization_tier=opt-balanced
user.sparetools.openssl:profile_id=autotools-lin-x86_64-gcc-static-std

