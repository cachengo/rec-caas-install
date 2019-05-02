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

%define COMPONENT instantiate
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 1.0.0
%define RPM_MINOR_VERSION 1

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service instantiate playbooks
License:        %{_platform_license}
BuildArch:      x86_64
Vendor:         %{_platform_vendor}
Source0:        %{name}-%{version}.tar.gz

%description
This rpm contains the necessary playbooks to instantiate the caas subsystem.

%prep
%autosetup

%build

%install
mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/app_install.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/caas_cleanup.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/cloud_admin_user.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/common.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/docker.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/image_push.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/openrc_hack.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/pre_config_all.yaml %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/app_install %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/caas_cleanup %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/cloud_admin_user %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/common_tasks %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/docker %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/docker_image_load %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/docker_image_push %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/manifests %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/nodeconf %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/pre_config_all %{buildroot}/%{_roles_path}/

mkdir -p %{buildroot}%_platform_etc_path/playbooks/bootstrapping/

mkdir -p %{buildroot}%/etc/lcm/playbooks/installation/provisioning/

mkdir -p %{buildroot}/etc/ansible/roles/plugins/filter/
rsync -av ansible/filter_plugins/* %{buildroot}/etc/ansible/roles/plugins/filter/

mkdir -p %{buildroot}/etc/ansible/roles/plugins/library/
rsync -av ansible/library/* %{buildroot}/etc/ansible/roles/plugins/library/

mkdir -p %{buildroot}/etc/cmframework/config
rsync -av cm_config/caas.yaml %{buildroot}/etc/cmframework/config/caas.yaml


%files
%{_playbooks_path}/*
%{_roles_path}/*
/etc/ansible/roles/plugins/filter/*
/etc/ansible/roles/plugins/library/*
/etc/cmframework/config/*


%preun

%post
mkdir -p %{_postconfig_path}/
ln -sf %{_playbooks_path}/app_install.yaml      %{_postconfig_path}/
ln -sf %{_playbooks_path}/cloud_admin_user.yaml %{_postconfig_path}/
ln -sf %{_playbooks_path}/common.yaml           %{_postconfig_path}/
ln -sf %{_playbooks_path}/docker.yaml           %{_postconfig_path}/
ln -sf %{_playbooks_path}/image_push.yaml       %{_postconfig_path}/
ln -sf %{_playbooks_path}/openrc_hack.yaml      %{_postconfig_path}/
ln -sf %{_playbooks_path}/pre_config_all.yaml   %{_postconfig_path}/

mkdir -p %{_finalize_path}/
ln -sf %{_playbooks_path}/caas_cleanup.yaml     %{_finalize_path}/

%postun
if [ $1 -eq 0 ]; then
    rm -f %{_postconfig_path}/app_install.yaml
    rm -f %{_postconfig_path}/cloud_admin_user.yaml
    rm -f %{_postconfig_path}/common.yaml
    rm -f %{_postconfig_path}/docker.yaml
    rm -f %{_postconfig_path}/image_push.yaml
    rm -f %{_postconfig_path}/openrc_hack.yaml
    rm -f %{_postconfig_path}/pre_config_all.yaml
    rm -f %{_finalize_path}/caas_cleanup.yaml
fi

%clean
rm -rf ${buildroot}
