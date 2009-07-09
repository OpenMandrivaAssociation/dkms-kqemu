%define module_name	kqemu
%define version	1.4.0
%define rel	7
%define snapshot	pre1
%define fullver	%{version}%{?snapshot:%{snapshot}}
%define dkmsver	%{fullver}-%{rel}
%define release	%mkrel %{?snapshot:0.%{snapshot}.}%{rel}
%ifarch %{ix86}
%define kqemu_program	qemu
%endif
%ifarch x86_64
%define kqemu_program	qemu-system-x86_64
%endif

Summary:	QEMU Accelerator Module
Name:		dkms-kqemu
Version:	%{version}
Release:	%{release}
Source0:	http://bellard.org/qemu/kqemu-%{fullver}.tar.gz
License:	GPL
URL:		http://bellard.org/qemu/
Group:		System/Kernel and hardware
Requires(post):	 dkms
Requires(preun): dkms
ExclusiveArch:	%{ix86} x86_64 
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
QEMU Accelerator (KQEMU) is a driver allowing the QEMU PC emulator to
run much faster when emulating a PC on an x86 host.

Full virtualization mode can also be enabled (with -kernel-kqemu) for
best performance. This mode only works with the following guest OSes:
Linux 2.4, Linux 2.6, Windows 2000 and Windows XP. WARNING: for
Windows 2000/XP, you cannot use it during installation.

Use "%{kqemu_program}" to benefit from the QEMU Accelerator Module.

%prep
%setup -q -n %{module_name}-%{fullver}

%build

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_usr}/src/%{module_name}-%{dkmsver}
tar cf - . | \
(cd $RPM_BUILD_ROOT%{_usr}/src/%{module_name}-%{dkmsver} && tar xf -)
cat > $RPM_BUILD_ROOT%{_usr}/src/%{module_name}-%{dkmsver}/dkms.conf << EOF
PACKAGE_NAME=%{module_name}
PACKAGE_VERSION=%{dkmsver}
MAKE[0]="./configure --kernel-path=/lib/modules/\${kernelver}/source && make"
DEST_MODULE_LOCATION[0]=/kernel/3rdparty/%{module_name}
BUILT_MODULE_NAME[0]=%{module_name}
AUTOINSTALL=yes
EOF

# install udev rules
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/
cat > $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/65-%{module_name}.rules << EOF
KERNEL=="%{module_name}", MODE="0666"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{module_name} -v %{kqemu_dkmsver}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{module_name} -v %{kqemu_dkmsver}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{module_name} -v %{kqemu_dkmsver}
/sbin/modprobe %{module_name} >/dev/null 2>&1 || :

%preun
# rmmod can fail
/sbin/rmmod %{module_name} >/dev/null 2>&1
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{module_name} -v %{kqemu_dkmsver} --all || :

%files
%defattr(-,root,root)
%doc README kqemu-doc.html kqemu-tech.html
%dir %{_usr}/src/%{module_name}-%{dkmsver}
%{_usr}/src/%{module_name}-%{dkmsver}/*
%_sysconfdir/udev/rules.d/65-%{module_name}.rules

