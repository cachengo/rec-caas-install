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

import os
import re
import subprocess

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: kubectl
version_added: "2.4"
short_description: Simply module to manage Kubernetes objects via manifest files
description:
- "Simply module to manage Kubernetes objects via manifest files"
options:
    manifest:
        description:
            - Path of manifest file describing Kubernetes object(s)
        required: true
        type: str
    kubeconfig:
        description:
            - Path of kubeconfig file used to connect apiserver
        required: false
        type: str
        default: ~/.kube/config
    timeout:
        description:
            - Max reauest timeout in seconds
        required: false
        type: int
        default: 5
    state:
        required: false
        default: present
        choices: ['present', 'absent']
author:
    - krisztian.lengyel@nokia.com
'''

EXAMPLES = '''
# Create a pod in Kubernetes
- name: Create pod
  kubectl:
    manifest: /home/kube_manifests/some-useful-pod.yaml
    state: present

# Delete some service
- name: Delete Kubernetes service
  kubectl:
    manifest: /home/kube_manifests/some-useless-svc.yaml
    kubeconfig: /home/admin-kubeconfig.yaml
    state: present

# Create many object from a single file
- name: Create stuffs
  kubectl:
    manifest: /home/kube_manifests/so-many-stuff.yaml
    timeout: 30
    state: present
'''

RETURN = '''
message:
    description: The output (stdout & stderr) of kubectl command
'''

STATE_MAPPING = {
    "present": "create",
    "absent": "delete"
}

ALREADY_EXIST_PATTERN = r'Error from server \(AlreadyExists\): error when creating .+ already exists'
SVC_IP_ALREADY_ALLOCATED_PATTERN = r'The Service .+ is invalid: .+ provided IP is already allocated'
NOT_FOUND_PATTERN = r'Error from server \(NotFound\): .+ not found'

KUBECONFIG_PATH = ".kube/config"


class KubectlExecutionError(Exception):
    pass


def main():
    module = _build_initialized_module()

    _add_defaults_to_params(module.params)

    try:
        result = _handle_module_result(*_execute_kubectl(module.params))
        module.exit_json(**result)
    except KubectlExecutionError as ex:
        module.fail_json(msg=str(ex))


def _build_initialized_module():
    module_args = dict(
        manifest=dict(required=True, type='str'),
        kubeconfig=dict(required=False, type='str'),
        timeout=dict(required=False, type='int', default=5),
        state=dict(required=False, choices=['present', 'absent'], type='str', default="present")
    )

    return AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )


def _add_defaults_to_params(params):
    if not params['kubeconfig']:
        params['kubeconfig'] = _get_default_kubeconfig_path()


def _get_default_kubeconfig_path():
    return "{}/{}".format(
        os.environ.get('HOME', ''),
        KUBECONFIG_PATH)


def _execute_kubectl(params):
    kubectl_command = STATE_MAPPING[params['state']]
    kubectl_cmd = ("/usr/bin/kubectl", kubectl_command) + _get_kubectl_flags(params)
    ansible_process = subprocess.Popen(kubectl_cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    return ansible_process.communicate()


def _get_kubectl_flags(flags):
    return ("--kubeconfig={}".format(flags['kubeconfig']),
            "--filename={}".format(flags['manifest']),
            "--request-timeout={}s".format(flags['timeout']))


def _handle_module_result(output, error):
    changed = _is_changed(error)
    if changed and error:
        raise KubectlExecutionError("Error: {}".format(error))

    return {
        'changed': changed,
        'message': output + error
    }


def _is_changed(message):
    if (re.search(ALREADY_EXIST_PATTERN, message)
            or re.search(SVC_IP_ALREADY_ALLOCATED_PATTERN, message)
            or re.search(NOT_FOUND_PATTERN, message)):
        return False
    return True


if __name__ == '__main__':
    main()
