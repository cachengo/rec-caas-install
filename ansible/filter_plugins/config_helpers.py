#!/usr/bin/python
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

from ansible.errors import AnsibleError
import itertools


class FilterModule(object):
    def filters(self):
        return {
            'extract_sriov_provider_network_interfaces': extract_sriov_provider_network_interfaces,
            'filter_network_profiles_by_type': filter_network_profiles_by_type,
            'filter_provider_networks_by_type': filter_provider_networks_by_type,
            'get_kube_options': get_kube_options,
            'get_mapped_key': get_mapped_key,
            'get_provider_networks': get_provider_networks,
        }


def extract_sriov_provider_network_interfaces(sriov_networks):
    return list(itertools.chain.from_iterable(
        [network.get('interfaces', [])
         for network in sriov_networks.itervalues()]))


def filter_network_profiles_by_type(profiles, key, type):
    return {name: profile for name, profile in profiles.iteritems()
            if key in profile and filter((lambda x: x.get('type', "") == type), profile[key].itervalues())}


def filter_provider_networks_by_type(profile, type):
    return {name: network for name, network in profile.iteritems()
            if network.get('type', "") == type}


def get_kube_options(options):
    _validate_dict(options)
    option_template = "{}={}"
    formated_options = [option_template.format(option, str(value))
                        for option, value in options.iteritems()]
    return ",".join(formated_options)


def get_mapped_key(mapping, search_key, key_name):
    _validate_dict(mapping)
    for key, value in mapping.iteritems():
        if (value.get(search_key, None) and
           value[search_key] == key_name):
            return key


def get_provider_networks(network_interfaces):
    return list(itertools.chain.from_iterable(
        [interface.get('provider_networks', [])
         for interface in network_interfaces.itervalues()]))


def _validate_dict(value):
    if not isinstance(value, dict):
        raise AnsibleError("Invalid type {}. Options must be dictionary!".format(type(value)))
