#!/usr/bin/python

# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

try:
    import shade
    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False

from distutils.version import StrictVersion


DOCUMENTATION = '''
---
module: os_dns_domain
short_description: Creates/removes DNS domains from OpenStack
extends_documentation_fragment: openstack
version_added: "2.0"
author: "Terry Howe (@terry_howe)"
description:
   - Add or remove DNS domain from OpenStack.
options:
   name:
     description:
        - Name of the domain.
     required: true
   state:
     description:
        - Desired state of the domain.
     required: false
     default: present
   ttl:
     description:
        - Time to live numeric value in seconds.
     required: true
   email:
     description:
        - Contact email address.
     required: false
     default: false
   description:
     description:
        - Text description.
     required: false
requirements: ["shade"]
'''

EXAMPLES = '''
# Create domain named 'example.com.'.
- os_dns_domain:
    state: present
    name: example.com.
    ttl: 3600
    email: admin@example.com
    description: Example domain
'''

RETURN = '''
dns_domain:
    description: Dictionary describing the domain.
    returned: On success when I(state) is 'present'.
    type: dictionary
    contains:
        id:
            description: Domain ID.
            type: string
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: Domain name.
            type: string
            sample: "example.com."
        ttl:
            description: Time to live.
            type: string
            sample: 3600
        email:
            description: Administrative contact email.
            type: string
            sample: "bob@example.com"
        description:
            description: Description of the domain.
            type: string
            sample: "Super awesome domain."
'''


def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(required=True),
        state=dict(default='present', choices=['absent', 'present']),
        ttl=dict(required=False, default=None),
        email=dict(required=False, default=None),
        description=dict(required=False, default=None),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    state = module.params['state']
    name = module.params['name']
    ttl = module.params['ttl']
    email = module.params['email']
    description = module.params['description']

    try:
        cloud = shade.openstack_cloud(**module.params)
        dom = cloud.get_zone(name)

        if state == 'present':
            if not dom:
                dom = cloud.create_zone(name, ttl=ttl, email=email,
                                        desription=description)
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed, dns_domain=dom, id=dom['id'])

        elif state == 'absent':
            if not dom:
                module.exit_json(changed=False)
            else:
                cloud.delete_zone(dom['id'])
                module.exit_json(changed=True)

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
if __name__ == "__main__":
    main()
