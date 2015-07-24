#!/usr/bin/python
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_subnet_lookup
short_description: Get the subnets ID's by tags.
description:
    - This module allows you to query for subnet ID's using tags. It is useful if you have to manage complex subnet structure and use modules that rely on subnet ID's given as comma separated values.
author: Piotr Mazurek
options:
  tags:
    description:
      - Tags by which you want to find the subnet ids.
    required: true
    default: null
    required: true
  region:
    description:
      - Region in which you want to lookup the subnets.
    required: true
    default: null
    required: true
extends_documentation_fragment: aws
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Get the subnet id's and register them in a variable.
- ec2_subnet_lookup:
    tags:
      Enviroment: Test
      Service: API
      Tier: Data
    region: eu-west-1
  register: subnets

- debug: var=subnets

It should return something similar to:

ok: [localhost] => {
    "var": {
        "subnets": {
            "changed": false,
            "invocation": {
                "module_args": "",
                "module_name": "subnet_lookup"
            },
            "subnet_ids": [
                "subnet-60f35517",
                "subnet-5c7e0d32",
                "subnet-62g56815"
            ]
        }
    }
}

Now this can be used in other modules that require subnet ID's as CSV's:
  some_module_value: {{subnets.subnet_ids | join(',')}}

'''

import sys

import boto.vpc
import boto.ec2

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            tags=dict(default=None, type='dict'),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    state = module.params.get('state')

    ec2_url, aws_access_key, aws_secret_key, region = get_ec2_creds(module)
    tags = module.params.get('tags')

    if region:
        try:
            vpc_conn = boto.vpc.connect_to_region(
                region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        except boto.exception.NoAuthHandlerFound, e:
            module.fail_json(msg = str(e))
    else:
        module.fail_json(msg="region must be specified")

    subnet_ids = []
    tag_filters = {
      'tag:' + tag: value
      for tag, value in tags.iteritems()
    }

    for subnet in vpc_conn.get_all_subnets(filters=tag_filters):
      subnet_ids.append(subnet.id)

    module.exit_json(changed=False, subnet_ids=subnet_ids)


# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>

from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

main()
