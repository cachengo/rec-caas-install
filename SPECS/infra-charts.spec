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

%define COMPONENT infra-charts
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 1.0.0
%define RPM_MINOR_VERSION 6

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service helm charts
License:        %{_platform_license}
BuildArch:      x86_64
Vendor:         %{_platform_vendor}
Source0:        %{name}-%{version}.tar.gz

Requires: rsync

%description
This rpm contains the necessary helm charts to deploy the caas subsystem.

%prep
%autosetup

%build

%install
mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/install_caas_infra.yaml %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/install_caas_infra %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/pre_install_caas_infra %{buildroot}/%{_roles_path}/

mkdir -p %{buildroot}/%{_caas_chart_path}/
rsync -av infra-charts/* %{buildroot}/%{_caas_chart_path}/

%files
%{_playbooks_path}/*
%{_roles_path}/*
%{_caas_chart_path}/*


%preun

%post
mkdir -p %{_postconfig_path}/
ln -sf %{_playbooks_path}/install_caas_infra.yaml %{_postconfig_path}/


%postun
if [ $1 -eq 0 ]; then
    rm -f %{_postconfig_path}/install_caas_infra.yaml
fi

%clean
rm -rf ${buildroot}
