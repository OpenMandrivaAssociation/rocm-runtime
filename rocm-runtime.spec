#Image support is x86 only
%ifarch %{x86_64}
%global enableimage 1
%endif
%global rocm_release %(echo %{version} |cut -d. -f1-2)
%global rocm_patch %(echo %{version} |cut -d. -f3-)

Name:       rocm-runtime
Version:    5.7.1
Release:    1
Summary:    ROCm Runtime Library
License:    NCSA
URL:        https://github.com/RadeonOpenCompute/ROCR-Runtime
Source0:    https://github.com/RadeonOpenCompute/ROCR-Runtime/archive/refs/tags/rocm-%{version}.tar.gz#/ROCR-Runtime-rocm-%{version}.tar.gz
Patch0:     rocm-runtime-no-.text-gc.patch
Patch1:     rocm-runtime-linkage.patch
#Patch0:     0002-fix-link-time-ordering-condition.patch

BuildRequires:  clang-devel
BuildRequires:  cmake
BuildRequires:	ninja
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(libhsakmt)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libffi)
BuildRequires:  cmake(LLD)
BuildRequires:  llvm-devel
BuildRequires:  rocm-device-libs
BuildRequires:  vim-common
BuildRequires:	xxd

%description
The ROCm Runtime Library is a thin, user-mode API that exposes the necessary
interfaces to access and interact with graphics hardware driven by the AMDGPU
driver set and the AMDKFD kernel driver. Together they enable programmers to
directly harness the power of AMD discrete graphics devices by allowing host
applications to launch compute kernels directly to the graphics hardware.

%package devel
Summary: ROCm Runtime development files
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: hsakmt(rocm) = %{rocm_release}

%description devel
ROCm Runtime development files

%prep
%autosetup -n ROCR-Runtime-rocm-%{version} -p1
#FIXME: rocm-device-libs cannot be found due to fedora changing install location
sed -i "s|\({CLANG_ARG_LIST}\)|\1 --hip-device-lib-path=%{_libdir}/amdgcn/bitcode|" \
	        src/image/blit_src/CMakeLists.txt \
	        src/core/runtime/trap_handler/CMakeLists.txt

cd src
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DINCLUDE_PATH_COMPATIBILITY=OFF \
    %{?!enableimage:-DIMAGE_SUPPORT=OFF} \
    -G Ninja

%build
%ninja_build -C src/build

%install
%ninja_install -C src/build

%files
%doc README.md
%license LICENSE.txt
%{_libdir}/libhsa-runtime64.so.1{,.*}
%exclude %{_docdir}/hsa-runtime64/LICENSE.md

%files devel
%{_includedir}/hsa/
%{_libdir}/libhsa-runtime64.so
%{_libdir}/cmake/hsa-runtime64/
