
%define pmc https://packages.microsoft.com

%define mib_name microsoft-identity-broker
%define mib_version 2.0.4
%define mib_path /ubuntu/24.04/prod/pool/main/m/%{mib_name}
%define mib_deb %{mib_name}_%{mib_version}_amd64.deb
%define mib_dir %{mib_name}-%{mib_version}

%define intune_name intune-portal
%define intune_version 1.2511.7
%define intune_path /ubuntu/24.04/prod/pool/main/i/%{intune_name}
%define intune_deb %{intune_name}_%{intune_version}-noble_amd64.deb
%define intune_dir %{intune_name}-%{intune_version}


Name:           unofficial-intune
Version:        0.0.4
Release:        1%{?dist}
Summary:        Dynamic rpm packager for intune
License:        GPLv3

# libs from f41, this version of intune unfortunately requires this for some reason
Source1:        libcrypto.so.3.2.6
Source2:        libssl.so.3.2.6
# additional files needed for intune to work correctly
Source3:        os-release
Source4:        common-password
Source5:        intune-portal
# systemd presets to force our stuff to be enabled
Source6:        75-unofficial-intune-system.preset
Source7:        75-unofficial-intune-user.preset

# for macros.pam
BuildRequires:  pam

BuildRequires:  systemd-rpm-macros
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires(pre):  wget >= 2

Requires:       java
Requires:       libpwquality
Requires:       microsoft-edge

Requires(post): dpkg
Requires(post): sed
Requires(post): /usr/bin/install
Requires(post): /usr/bin/mktemp

Requires(postun): sed

%description
Dynamic rpm packager for intune

%install
install -d %{buildroot}%{_datarootdir}/%{name}-%{version}/debs
install -d %{buildroot}%{_datarootdir}/%{name}-%{version}/logs
install -d %{buildroot}/opt/microsoft/identity-broker/bin
install -d %{buildroot}/opt/microsoft/intune/bin
install -d %{buildroot}/opt/microsoft/intune/share/locale
install -D -m 0755 -t %{buildroot}/opt/microsoft/intune/lib %{SOURCE1} %{SOURCE2}
install -D -m 0644 -t %{buildroot}/opt/microsoft/intune/etc %{SOURCE3}
install -D -m 0644 -t %{buildroot}%{_pam_confdir} %{SOURCE4}
install -D -m 0755 -t %{buildroot}%{_bindir} %{SOURCE5}
install -D -m 0644 -t %{buildroot}%{_presetdir} %{SOURCE6}
install -D -m 0644 -t %{buildroot}%{_userpresetdir} %{SOURCE7}

%pre
install -d %{_datarootdir}/%{name}-%{version}/logs
{
wget -O %{_datarootdir}/%{name}-%{version}/debs/%{mib_deb} "%{pmc}/%{mib_path}/%{mib_deb}"
wget -O %{_datarootdir}/%{name}-%{version}/debs/%{intune_deb} "%{pmc}/%{intune_path}/%{intune_deb}"
} > %{_datarootdir}/%{name}-%{version}/logs/pre.log

%post
{
TMPDIR=$(mktemp -d)
pushd ${TMPDIR}

dpkg-deb -x %{_datarootdir}/%{name}-%{version}/debs/%{mib_deb} %{mib_dir}
install -D -m 0755 %{mib_dir}/opt/microsoft/identity-broker/bin/microsoft-identity-broker /opt/microsoft/identity-broker/bin/microsoft-identity-broker
install -D -m 0755 %{mib_dir}/opt/microsoft/identity-broker/bin/microsoft-identity-device-broker /opt/microsoft/identity-broker/bin/microsoft-identity-device-broker
install -D -m 0644 %{mib_dir}/usr/lib/systemd/system/microsoft-identity-device-broker.service /usr/lib/systemd/system/microsoft-identity-device-broker.service
install -D -m 0644 %{mib_dir}/usr/share/applications/microsoft-identity-broker.desktop /usr/share/applications/microsoft-identity-broker.desktop
install -D -m 0644 %{mib_dir}/usr/share/dbus-1/services/com.microsoft.identity.broker1.service /usr/share/dbus-1/services/com.microsoft.identity.broker1.service
install -D -m 0644 %{mib_dir}/usr/share/dbus-1/system-services/com.microsoft.identity.devicebroker1.service /usr/share/dbus-1/system-services/com.microsoft.identity.devicebroker1.service
install -D -m 0644 %{mib_dir}/usr/share/dbus-1/system.d/com.microsoft.identity.devicebroker1.conf /usr/share/dbus-1/system.d/com.microsoft.identity.devicebroker1.conf
install -D -m 0644 %{mib_dir}/usr/share/icons/hicolor/256x256/apps/microsoft-identity-broker.png /usr/share/icons/hicolor/256x256/apps/microsoft-identity-broker.png
rm -rf "%{mib_dir}"

dpkg-deb -x %{_datarootdir}/%{name}-%{version}/debs/%{intune_deb} %{intune_dir}

# We need to replace the path to use our binary in /usr/bin since it wraps the real binary
sed -i -e 's,/opt/microsoft/intune/bin/intune-portal,/usr/bin/intune-portal,' %{intune_dir}/usr/share/applications/intune-portal.desktop

install -D -m 0644 %{intune_dir}/usr/share/pam-configs/intune /usr/share/pam-configs/intune
install -D -m 0644 %{intune_dir}/usr/share/applications/intune-portal.desktop /usr/share/applications/intune-portal.desktop
install -D -m 0644 %{intune_dir}/usr/share/icons/hicolor/48x48/apps/intune.png /usr/share/icons/hicolor/48x48/apps/intune.png
install -D -m 0644 %{intune_dir}/usr/share/polkit-1/actions/com.microsoft.intune.policy /usr/share/polkit-1/actions/com.microsoft.intune.policy
install -D -m 0644 %{intune_dir}/usr/share/doc/intune-portal/copyright /usr/share/doc/intune-portal/copyright
install -D -m 0644 %{intune_dir}/usr/lib/tmpfiles.d/intune.conf /usr/lib/tmpfiles.d/intune.conf
install -D -m 0755 %{intune_dir}/usr/lib/x86_64-linux-gnu/security/pam_intune.so /usr/lib/x86_64-linux-gnu/security/pam_intune.so
install -D -m 0644 %{intune_dir}/opt/microsoft/intune/NOTICE.txt /opt/microsoft/intune/NOTICE.txt
install -D -m 0755 %{intune_dir}/opt/microsoft/intune/bin/intune-agent /opt/microsoft/intune/bin/intune-agent
install -D -m 0755 %{intune_dir}/opt/microsoft/intune/bin/intune-daemon /opt/microsoft/intune/bin/intune-daemon
install -D -m 0755 %{intune_dir}/opt/microsoft/intune/bin/intune-portal /opt/microsoft/intune/bin/intune-portal
install -D -m 0644 %{intune_dir}/lib/systemd/system/intune-daemon.service /lib/systemd/system/intune-daemon.service
install -D -m 0644 %{intune_dir}/lib/systemd/system/intune-daemon.socket /lib/systemd/system/intune-daemon.socket
install -D -m 0644 %{intune_dir}/lib/systemd/user/intune-agent.service /lib/systemd/user/intune-agent.service
install -D -m 0644 %{intune_dir}/lib/systemd/user/intune-agent.timer /lib/systemd/user/intune-agent.timer
for lang in $(ls %{intune_dir}/opt/microsoft/intune/share/locale); do
    install -D -m 0644 %{intune_dir}/opt/microsoft/intune/share/locale/${lang}/LC_MESSAGES/intune.mo /opt/microsoft/intune/share/locale/${lang}/LC_MESSAGES/intune.mo
done
rm -rf "%{intune_dir}"

popd
rmdir ${TMPDIR}
} > %{_datarootdir}/%{name}-%{version}/logs/post.log

grep -q graph.microsoft.com /etc/hosts || echo "20.190.152.24 graph.microsoft.com" >> /etc/hosts

%systemd_post microsoft-identity-device-broker.service intune-daemon.socket
%systemd_user_post intune-agent.timer

%preun
%systemd_preun microsoft-identity-device-broker.service intune-daemon.socket
%systemd_user_preun intune-agent.timer

rm -f /opt/microsoft/intune/share/locale/*/LC_MESSAGES/intune.mo
rmdir /opt/microsoft/intune/share/locale/*/LC_MESSAGES
rmdir /opt/microsoft/intune/share/locale/*

%postun
%systemd_postun microsoft-identity-device-broker.service intune-daemon.socket
%systemd_user_postun intune-agent.timer

sed -i -e '/20.190.152.24 graph.microsoft.com/d' /etc/hosts

%files
/opt/microsoft/identity-broker
/opt/microsoft/intune
%{_pam_confdir}/common-password
%{_bindir}/intune-portal
%{_presetdir}/75-unofficial-intune-system.preset
%{_userpresetdir}/75-unofficial-intune-user.preset

%{_datarootdir}/%{name}-%{version}
%ghost %{_datarootdir}/%{name}-%{version}/logs/pre.log
%ghost %{_datarootdir}/%{name}-%{version}/logs/post.log
%ghost %{_datarootdir}/%{name}-%{version}/debs/%{mib_deb}
%ghost %{_datarootdir}/%{name}-%{version}/debs/%{intune_deb}

%ghost /opt/microsoft/identity-broker/bin/microsoft-identity-broker
%ghost /opt/microsoft/identity-broker/bin/microsoft-identity-device-broker
%ghost /usr/lib/systemd/system/microsoft-identity-device-broker.service
%ghost /usr/share/applications/microsoft-identity-broker.desktop
%ghost /usr/share/dbus-1/services/com.microsoft.identity.broker1.service
%ghost /usr/share/dbus-1/system-services/com.microsoft.identity.devicebroker1.service
%ghost /usr/share/dbus-1/system.d/com.microsoft.identity.devicebroker1.conf
%ghost /usr/share/icons/hicolor/256x256/apps/microsoft-identity-broker.png

%ghost /usr/share/pam-configs/intune
%ghost /usr/share/applications/intune-portal.desktop
%ghost /usr/share/icons/hicolor/48x48/apps/intune.png
%ghost /usr/share/polkit-1/actions/com.microsoft.intune.policy
%ghost /usr/share/doc/intune-portal/copyright
%ghost /usr/lib/tmpfiles.d/intune.conf
%ghost /usr/lib/x86_64-linux-gnu/security/pam_intune.so
%ghost /opt/microsoft/intune/NOTICE.txt
%ghost /opt/microsoft/intune/bin/intune-agent
%ghost /opt/microsoft/intune/bin/intune-daemon
%ghost /opt/microsoft/intune/bin/intune-portal
%ghost /lib/systemd/system/intune-daemon.service
%ghost /lib/systemd/system/intune-daemon.socket
%ghost /lib/systemd/user/intune-agent.service
%ghost /lib/systemd/user/intune-agent.timer


%changelog
* Wed Feb 18 2026 Dan Streetman <ddstreet@ieee.org> - 0.0.4-1
- something, something, certificate blah blah, something

* Wed Feb 18 2026 Dan Streetman <ddstreet@ieee.org> - 0.0.3-1
- fix systemd unit handling in post

* Wed Feb 18 2026 ddstreet
- 
