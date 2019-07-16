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
%define RPM_MINOR_VERSION 10

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service instantiate playbooks
License:        %{_platform_license}
BuildArch:      x86_64
Vendor:         %{_platform_vendor}
Source0:        %{name}-%{version}.tar.gz

Requires: rsync

%description
This rpm contains the necessary playbooks to instantiate the caas subsystem.

%prep
%autosetup

%build

%install
mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/caas_cleanup.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/cloud_admin_user.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/common.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/docker.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/image_push.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/openrc_hack.yaml %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/pre_config_all.yaml %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/caas_cleanup %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/cloud_admin_user %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/common_tasks %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/docker %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/docker_image_load %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/docker_image_push %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/manifests %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/nodeconf %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/pre_config_all %{buildroot}/%{_roles_path}/

mkdir -p %{buildroot}%/%{_bootstrapping_path}/

mkdir -p %{buildroot}%/%{_provisioning_path}/

mkdir -p %{buildroot}/%{_ansible_filter_plugins_path}/
rsync -av ansible/filter_plugins/* %{buildroot}/%{_ansible_filter_plugins_path}/

mkdir -p %{buildroot}/%{_ansible_modules_path}/
rsync -av ansible/library/* %{buildroot}/%{_ansible_modules_path}/

mkdir -p %{buildroot}/%{_cm_config_dir}
rsync -av cm_config/caas.yaml %{buildroot}/%{_cm_caas_config_file}

# Set build variable to CaaS config
## Rename variable
sed -ri 's/^crf_chart_path/caas_chart_path/' %{buildroot}/%{_cm_caas_config_file}

## Set config values
sed -ri '/^caas_base_directory/{s|:.*|: %{_caas_path}|}'                       %{buildroot}/%{_cm_caas_config_file}
sed -ri '/^infra_containers_directory/{s|:.*|: %{_caas_container_tar_path}|}'  %{buildroot}/%{_cm_caas_config_file}
sed -ri '/^manifests_directory/{s|:.*|: %{_caas_manifest_path}|}'              %{buildroot}/%{_cm_caas_config_file}
sed -ri '/^rbac_manifests_directory/{s|:.*|: %{_caas_rbac_manifests_path}|}'   %{buildroot}/%{_cm_caas_config_file}
sed -ri '/^caas_chart_path/{s|:.*|: %{_caas_chart_path}|}'                     %{buildroot}/%{_cm_caas_config_file}
sed -ri '/^libexec_dir/{s|:.*|: %{_caas_libexec_path}|}'                       %{buildroot}/%{_cm_caas_config_file}
sed -ri '/^danm_crd_dir/{s|:.*|: %{_caas_danm_crd_path}|}'                     %{buildroot}/%{_cm_caas_config_file}

%files
%{_playbooks_path}/*
%{_roles_path}/*
%{_ansible_filter_plugins_path}/*
%{_ansible_modules_path}/*
%{_cm_config_dir}/*


%preun

%post
mkdir -p %{_postconfig_path}/
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
