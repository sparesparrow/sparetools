include(default)

[settings]
os=Windows
arch=x86_64
compiler=msvc
compiler.version=193
compiler.cppstd=17
compiler.runtime=dynamic
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
user.sparetools.openssl:target=VC-WIN64A
user.sparetools.openssl:openssl_release=v3_3_2
user.sparetools.openssl:optimization_tier=opt-balanced
user.sparetools.openssl:profile_id=perl-win-x86_64-msvc-shared-std
