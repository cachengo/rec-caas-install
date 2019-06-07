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


class FilterModule(object):
    def filters(self):
        return {
            'get_kube_options': get_kube_options,
            'get_mapped_key': get_mapped_key,
        }


def get_kube_options(options):
    if not isinstance(options, dict):
        raise AnsibleError("Invalid type {}. Options must be dictionary!".format(type(options)))

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


def _validate_dict(value):
    if not isinstance(value, dict):
        raise AnsibleError("Invalid type {}. Options must be dictionary!".format(type(options)))
