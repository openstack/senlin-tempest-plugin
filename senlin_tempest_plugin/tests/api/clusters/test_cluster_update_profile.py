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

import copy
from tempest.lib import decorators

from senlin_tempest_plugin.common import constants
from senlin_tempest_plugin.common import utils
from senlin_tempest_plugin.tests.api import base


class TestClusterUpdateProfile(base.BaseSenlinAPITest):

    def setUp(self):
        super(TestClusterUpdateProfile, self).setUp()

        self.old_profile_id = utils.create_a_profile(self)
        self.addCleanup(utils.delete_a_profile, self, self.old_profile_id)

        # create a new profile
        new_spec = copy.deepcopy(constants.spec_nova_server)
        new_spec['properties']['flavor'] = 'new_flavor'
        new_spec['properties']['image'] = 'new_image'
        self.new_profile_id = utils.create_a_profile(self, new_spec)
        self.addCleanup(utils.delete_a_profile, self, self.new_profile_id)

        self.cluster_id = utils.create_a_cluster(self, self.old_profile_id)
        self.addCleanup(utils.delete_a_cluster, self, self.cluster_id)

        self.node1_id = utils.create_a_node(
            self, self.old_profile_id, name='N01', cluster_id=self.cluster_id)
        # The following logic is not needed, when cluster is deleted, the
        # node is deleted automatially.
        # self.addCleanup(utils.delete_a_node, self, self.node1_id)

    @decorators.idempotent_id('abff7891-21af-4c37-a8df-5bc7379ce349')
    def test_cluster_update_profile(self):
        # Update cluster with new profile
        params = {
            'cluster': {
                'profile_id': self.new_profile_id
            }
        }
        res = self.client.update_obj('clusters', self.cluster_id, params)

        # Verify resp of cluster update API
        self.assertEqual(202, res['status'])
        self.assertIsNotNone(res['body'])
        self.assertIn('actions', res['location'])
        cluster = res['body']
        for key in ['created_at', 'data', 'domain', 'id', 'init_at',
                    'metadata', 'name', 'nodes', 'policies', 'profile_id',
                    'profile_name', 'project', 'status', 'status_reason',
                    'timeout', 'updated_at', 'user']:
            self.assertIn(key, cluster)

        # Wait for cluster update to be done before moving on
        action_id = res['location'].split('/actions/')[1]
        self.client.wait_for_status('actions', action_id, 'SUCCEEDED')

    @utils.api_microversion('1.6')
    @decorators.idempotent_id('686cd38a-16eb-4364-b495-367fc7c8bb26')
    def test_cluster_update_profile_profile_only(self):
        # Update cluster with new profile
        params = {
            'cluster': {
                'profile_id': self.new_profile_id,
                'profile_only': True
            }
        }
        res = self.client.update_obj('clusters', self.cluster_id, params)

        # Verify resp of cluster update API
        self.assertEqual(202, res['status'])
        self.assertIsNotNone(res['body'])
        self.assertIn('actions', res['location'])

        # Wait for cluster update to be done before moving on
        action_id = res['location'].split('/actions/')[1]
        self.client.wait_for_status('actions', action_id, 'SUCCEEDED')

        # verify cluster profile id changed
        res = self.client.get_obj('clusters', self.cluster_id)
        self.assertEqual(self.new_profile_id, res['body']['profile_id'])

        # verify node profile id not changed.
        res = self.client.get_obj('nodes', self.node1_id)
        self.assertEqual(self.old_profile_id, res['body']['profile_id'])

    @utils.api_microversion('1.5')
    @decorators.idempotent_id('8a67876f-e9ea-4cbe-807a-73eefe482536')
    def test_cluster_update_profile_profile_only_backward(self):
        # Update cluster with new profile
        params = {
            'cluster': {
                'profile_id': self.new_profile_id,
                'profile_only': True
            }
        }
        res = self.client.update_obj('clusters', self.cluster_id, params)

        # Verify resp of cluster update API
        self.assertEqual(202, res['status'])
        self.assertIsNotNone(res['body'])
        self.assertIn('actions', res['location'])

        # Wait for cluster update to be done before moving on
        action_id = res['location'].split('/actions/')[1]
        self.client.wait_for_status('actions', action_id, 'SUCCEEDED')

        # verify cluster profile id changed
        res = self.client.get_obj('clusters', self.cluster_id)
        self.assertEqual(self.new_profile_id, res['body']['profile_id'])

        # verify node profile id not changed.
        res = self.client.get_obj('nodes', self.node1_id)
        self.assertEqual(self.new_profile_id, res['body']['profile_id'])
