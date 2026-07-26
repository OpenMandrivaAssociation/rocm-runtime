# cmake.req scans for find_dependency(LibElf) even though that branch is
# dead for the shared-library build (_is_hsa_runtime_dynamic = ON).
%global __requires_exclude cmake\\([Ll]ib[Ee]lf\\)

Name:		rocm-runtime
Version:	7.14.0
Release:	1
%{!?rocm_llvm_maj_ver:%global rocm_llvm_maj_ver 23}
Summary:	ROCm Runtime Library (ROCR / HSA)
License:	NCSA
Group:		System/Libraries
URL:		https://github.com/ROCm/rocm-systems
Source0:	https://github.com/ROCm/rocm-systems/releases/download/therock-7.14/rocr-runtime.tar.gz#/rocr-runtime-%{version}.tar.gz
# SI/CI/VI (r800) addrlib HWL removed in ROCm 7; taken from ROCR-Runtime rocm-6.4.4
Source1:	r800-addrlib-rocm-6.4.4.tar.gz
Patch0:		0001-device-lib-path.patch
Patch1:		0002-no-gc-sections-trap.patch
Patch2:		0003-no-gc-sections-blit.patch
# Restore DoorbellType 0/1 (Polaris/gfx803 etc.) removed upstream in 0d70045817
Patch3:		0004-restore-legacy-doorbell-type-0-1.patch
# Soft-skip image manager if addrlib init still fails (fallback)
Patch4:		0005-skip-image-support-pre-gfx9.patch
# Wire r800 (SI/CI/VI) addrlib back into Create() + CMakeLists
Patch5:		0006-restore-r800-addrlib-images.patch
# Clamp 1D height/slices for v1 addrlib; don't assert on zero size
Patch6:		0007-gfx8-image-dim-clamp.patch
# GFX8 mipmaps: BASE_LEVEL/LAST_LEVEL SRDs + addrlib numMipLevels
Patch7:		0008-gfx8-restore-mipmaps.patch
# Allow mip level views on GFX8; set basePitch for SI+ mip size calc
Patch8:		0009-gfx8-mip-level-views.patch
# Sum per-level sizes for mip chains (ADDR v1 only sizes one level)
Patch9:		0010-gfx8-mip-chain-size.patch

%ifarch %{x86_64}
%global enableimage 1
%endif

BuildRequires:	rocm-rpm-macros
BuildRequires:	clang >= %{rocm_llvm_maj_ver}
BuildRequires:	lib64clang-devel >= %{rocm_llvm_maj_ver}
BuildRequires:	lib64llvm-devel >= %{rocm_llvm_maj_ver}
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(libelf)
BuildRequires:	pkgconfig(libdrm)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(numa)
BuildRequires:	lib64lld-devel
BuildRequires:	rocm-device-libs
BuildRequires:	rocprofiler-register
BuildRequires:	xxd
BuildRequires:	vim-common

Obsoletes:	%{mklibname hsakmt 1} < %{EVRD}
Provides:	%{mklibname hsakmt 1} = %{EVRD}

ExclusiveArch:	%{x86_64} %{aarch64}

%description
The ROCm Runtime Library (libhsa-runtime64) is a thin, user-mode API that
exposes interfaces to access graphics hardware driven by the AMDGPU driver
and AMDKFD. The former hsakmt thunk is included. Built from TheRock 7.14
sources.

OpenMandriva restores pre-Vega support that upstream ROCm 7 removed:
- doorbell types 0/1 (Polaris/gfx803 queue rings)
- r800 addrlib HWL from ROCm 6.4.4 for SI/CI/VI image/texture layout

LLVM still supports gfx803, so this enables compute and basic image testing
on older AMD GPUs without new hardware.

%package devel
Summary:	ROCm Runtime development files
Group:		Development/C
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	pkgconfig(libelf)
Obsoletes:	%{mklibname -d hsakmt} < %{EVRD}
Provides:	%{mklibname -d hsakmt} = %{EVRD}

%description devel
Headers and CMake packages for the ROCm HSA runtime.

%prep
%autosetup -n rocr-runtime -p1
# r800 HWL sources (not in TheRock 7.14 tarball)
tar -xzf %{SOURCE1} -C runtime/hsa-runtime/image/addrlib/src
test -f runtime/hsa-runtime/image/addrlib/src/r800/ciaddrlib.cpp
sed -i -e 's|@ROCM_DEVICE_LIB_PATH@|%{_libdir}/amdgcn/bitcode|g' \
	runtime/hsa-runtime/image/blit_src/CMakeLists.txt

%cmake \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	%{?!enableimage:-DIMAGE_SUPPORT=OFF} \
	-G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build
# Shared build never needs LibElf for consumers; cmake.req still scans the string.
# Remove the dead branch so packaging and consumers stay clean.
sed -i -e '/find_dependency(LibElf)/d' \
	%{buildroot}%{_libdir}/cmake/hsa-runtime64/hsa-runtime64-config.cmake

%files
%doc README.md
%license LICENSE.txt
%{_libdir}/libhsa-runtime64.so.1{,.*}
%exclude %{_docdir}/rocr/LICENSE.md

%files devel
%{_includedir}/hsa/
%{_includedir}/hsakmt/
%{_libdir}/libhsa-runtime64.so
%{_libdir}/libhsakmt.a
%{_libdir}/cmake/hsa-runtime64/
%{_libdir}/cmake/hsakmt/
%{_libdir}/pkgconfig/libhsakmt.pc
