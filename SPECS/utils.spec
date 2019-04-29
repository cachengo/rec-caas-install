# Copyright 2019 Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%define COMPONENT utils
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 1.0.0
%define RPM_MINOR_VERSION 1
%define KUBELET_PLUGINS_LOGDIR /var/log/kubelet-plugins/

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service supplementary utils
License:        %{_platform_license}
BuildArch:      x86_64
Vendor:         %{_platform_vendor}
Source0:        %{name}-%{version}.tar.gz

Requires: initscripts

%description
This rpm contains the supplementary utils for caas subsystem.

%prep

%autosetup

%build

%install
mkdir -p %{buildroot}/%{_caas_libexec_path}/
# --------------------------- LOG
mkdir -p %{buildroot}/etc/logrotate.d/
install -m 0640 utils/log/kubelet-plugins %{buildroot}/etc/logrotate.d/
sed -i -e 's|{{ kubelet_plugings_log_dir }}|%{KUBELET_PLUGINS_LOGDIR}|g' %{buildroot}/etc/logrotate.d/kubelet-plugins
# --------------------------- DEPLOY
install -m 0700 utils/deploy/merge_image.sh %{buildroot}/%{_caas_libexec_path}/
mkdir -p %{buildroot}/etc/systemd/system/
# --------------------------- COMMON
mkdir -p %{buildroot}/etc/profile.d/
install -m 0644 utils/common/aliases.sh %{buildroot}/etc/profile.d/

%files
%{_caas_libexec_path}/merge_image.sh
/etc/profile.d/aliases.sh
/etc/logrotate.d/kubelet-plugins
%exclude %{_caas_libexec_path}/*pyc
%exclude %{_caas_libexec_path}/*pyo

%preun

%post
# --------------------------- LOG
mkdir -p %{KUBELET_PLUGINS_LOGDIR}/
grep "#CaaS CUSTOM BEGIN" /etc/logrotate.d/syslog > /dev/null;
if [ $? -eq 0 ]; then
  sed -i -e '/#CaaS CUSTOM BEGIN/,/#CaaS CUSTOM END/d' /etc/logrotate.d/syslog
  fi
sed -i.bak -e '/.*missingok/i #CaaS CUSTOM BEGIN\n    hourly\n    size 50\n#CaaS CUSTOM END' /etc/logrotate.d/syslog
# --------------------------- DEPLOY
find /usr/lib/debug/usr/ -xtype l -exec rm -f {} \;
# --------------------------- COMMON

%postun
# If not upgrade, revert all CaaS related cusotmization
if [ $1 == 0 ]; then

# --------------------------- LOG
  sed -i -e '/#CaaS CUSTOM BEGIN/,/#CaaS CUSTOM END/d' /etc/logrotate.d/syslog
/usr/bin/systemctl daemon-reload
# --------------------------- DEPLOY
# --------------------------- COMMON
  rm -rf /etc/profile.d/aliases.sh

fi


%clean
rm -rf ${buildroot}
