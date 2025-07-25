%global __requires_exclude ^.*libelf.*$ 

#Image support is x86 only
%ifarch %{x86_64}
%global enableimage 1
%endif
%global rocm_release %(echo %{version} |cut -d. -f1-2)
%global rocm_patch %(echo %{version} |cut -d. -f3-)

Name:       rocm-runtime
Version:    6.3.3
Release:    1
Summary:    ROCm Runtime Library
License:    NCSA
URL:        https://github.com/ROCm/ROCR-Runtime
Source0:    https://github.com/ROCm/ROCR-Runtime/archive/refs/tags/rocm-%{version}.tar.gz#/ROCR-Runtime-rocm-%{version}.tar.gz

BuildRequires:  clang-devel
BuildRequires:  cmake
BuildRequires:	ninja
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libffi)
BuildRequires:	pkgconfig(numa)
BuildRequires:  cmake(LLD)
BuildRequires:  llvm-devel
BuildRequires:  rocm-device-libs
BuildRequires:  vim-common
BuildRequires:	xxd

Obsoletes:	%{mklibname hsakmt 1} < %{EVRD}

%patchlist
rocm-runtime-no-.text-gc.patch
rocm-runtime-aarch64.patch

%description
The ROCm Runtime Library is a thin, user-mode API that exposes the necessary
interfaces to access and interact with graphics hardware driven by the AMDGPU
driver set and the AMDKFD kernel driver. Together they enable programmers to
directly harness the power of AMD discrete graphics devices by allowing host
applications to launch compute kernels directly to the graphics hardware.

%package devel
Summary: ROCm Runtime development files
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: %{mklibname -d hsakmt} < %{EVRD}

%description devel
ROCm Runtime development files

%prep
%autosetup -n ROCR-Runtime-rocm-%{version} -p1
export OCL_BITCODE_DIR=%{_libdir}/amdgcn/bitcode
sed -i -e 's,-cl-std=CL2.0,-cl-std=CL2.0 --hip-device-lib-path=%{_libdir}/amdgcn/bitcode,g' runtime/hsa-runtime/image/blit_src/CMakeLists.txt

%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DINCLUDE_PATH_COMPATIBILITY=OFF \
    %{?!enableimage:-DIMAGE_SUPPORT=OFF} \
    -G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build

%files
%doc README.md
%license LICENSE.txt
%{_libdir}/libhsa-runtime64.so.1{,.*}
%exclude %{_docdir}/hsa-runtime64/LICENSE.md

%files devel
%{_includedir}/hsa/
%{_includedir}/hsakmt/
%{_libdir}/libhsa-runtime64.so
%{_libdir}/cmake/hsa-runtime64/
%{_libdir}/cmake/hsakmt/
%{_libdir}/libhsakmt.a
%{_libdir}/pkgconfig/libhsakmt.pc
