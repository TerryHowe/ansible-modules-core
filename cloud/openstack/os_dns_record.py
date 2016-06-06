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
module: os_dns_record
short_description: Creates/removes DNS domain records from OpenStack
extends_documentation_fragment: openstack
version_added: "2.0"
author: "Terry Howe (@terry_howe)"
description:
   - Add or remove DNS domain record from OpenStack.
options:
   name:
     description:
        - Name of the record.
     required: true
   state:
     description:
        - Desired state of the domain.
     required: false
     default: present
   domain:
     description:
        - Domain for the record.
     required: true
   type:
     description:
        - Type of DNS record.
     required: true
   data:
     description:
        - Data associated with record.
     required: true
   description:
     description:
        - Description of record.
     required: false
requirements: ["shade"]
'''

EXAMPLES = '''
# Create record A record 'www' in 'example.com.'.
- os_dns_record:
    state: present
    name: www
    domain: example.com.
    type: A
    data:
        - 192.168.1.2
'''

RETURN = '''
dns_record:
    description: Dictionary describing the DNS record.
    returned: On success when I(state) is 'present'.
    type: dictionary
    contains:
        id:
            description: Record ID.
            type: string
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: Record name.
            type: string
            sample: "www"
        type:
            description: Record type.
            type: string
            sample: A
        data:
            description: Data associated with the record.
            type: string
            sample: "192.168.1.2"
        description:
            description: Description of the record.
            type: string
            sample: "World wide web for example.com."
'''


def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(required=True),
        state=dict(default='present', choices=['absent', 'present']),
        domain=dict(required=True),
        type=dict(required=True),
        data=dict(required=True),
        description=dict(required=False, default=None),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    state = module.params['state']
    name = module.params['name']
    domain = module.params['domain']
    record_type = module.params['type']
    data = module.params['data']
    description = module.params['description']

    try:
        cloud = shade.openstack_cloud(**module.params)
        record = cloud.get_recordset(domain, name)

        if state == 'present':
            if not record:
                record = cloud.create_recordset(domain, name, record_type,
                                                data, description)
                changed = True
            else:
                changed = False
                if description is not None:
                    if description == record['description']:
                        changed = True
                if data is not None:
                    if data == record['data']:
                        changed = True
                if changed:
                    record = cloud.update_recordset(domain, name, records=data,
                                                    description=description)
            module.exit_json(changed=changed, dns_record=record,
                             id=record['id'])

        elif state == 'absent':
            if not record:
                module.exit_json(changed=False)
            else:
                cloud.delete_dns_record(domain, record['id'])
                module.exit_json(changed=True)

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
if __name__ == "__main__":
    main()
