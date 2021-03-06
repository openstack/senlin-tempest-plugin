# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from tempest.lib import decorators

from senlin_tempest_plugin.common import utils
from senlin_tempest_plugin.tests.api import base


class TestNodeCreate(base.BaseSenlinAPITest):

    def setUp(self):
        super(TestNodeCreate, self).setUp()
        self.profile_id = utils.create_a_profile(self)
        self.addCleanup(utils.delete_a_profile, self, self.profile_id)
        self.cluster_id = utils.create_a_cluster(
            self, self.profile_id,
            config={'node.name.format': 'test-node'})
        self.addCleanup(utils.delete_a_cluster, self, self.cluster_id)

    @utils.api_microversion('1.0')
    @decorators.idempotent_id('14d06753-7f0a-4ad2-84be-37fce7114a8f')
    def test_node_create_all_attrs_defined(self):
        expected_keys = ['cluster_id', 'created_at', 'data', 'domain', 'id',
                         'index', 'init_at', 'metadata', 'name', 'physical_id',
                         'profile_id', 'profile_name', 'project', 'role',
                         'status', 'status_reason', 'updated_at', 'user']
        self._create_node(expected_keys)

    @decorators.idempotent_id('b678a196-01bf-42cb-a079-9595d937d211')
    @utils.api_microversion('1.13')
    def test_node_create_all_attrs_defined_v1_13(self):
        expected_keys = ['cluster_id', 'created_at', 'data', 'domain', 'id',
                         'index', 'init_at', 'metadata', 'name', 'physical_id',
                         'profile_id', 'profile_name', 'project', 'role',
                         'status', 'status_reason', 'tainted',
                         'updated_at', 'user']
        self._create_node(expected_keys)

    def _create_node(self, expected_keys):
        params = {
            'node': {
                'profile_id': self.profile_id,
                'cluster_id': self.cluster_id,
                'metadata': {'k1': 'v1'},
                'role': 'member',
                'name': 'test-node'
            }
        }
        res = self.client.create_obj('nodes', params)

        # Verify resp of node create API
        self.assertEqual(202, res['status'])
        self.assertIsNotNone(res['body'])
        self.assertIn('actions', res['location'])
        node = res['body']
        self.addCleanup(utils.delete_a_node, self, node['id'])
        for key in expected_keys:
            self.assertIn(key, node)
        self.assertIn('test-node', node['name'])
        self.assertEqual(self.profile_id, node['profile_id'])
        self.assertEqual(self.cluster_id, node['cluster_id'])
        self.assertEqual({'k1': 'v1'}, node['metadata'])
        self.assertEqual('member', node['role'])
        self.assertEqual('test-node', node['name'])

        # Wait node to be active before moving on
        action_id = res['location'].split('/actions/')[1]
        self.client.wait_for_status('actions', action_id, 'SUCCEEDED')
