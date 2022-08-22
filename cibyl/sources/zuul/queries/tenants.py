"""
#    Copyright 2022 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
import logging

from cibyl.sources.zuul.transactions import TenantsRequest

LOG = logging.getLogger(__name__)


def perform_tenants_query(zuul, **kwargs):
    """Query for tenants.

    :param zuul: API to interact with Zuul with.
    :type zuul: :class:`cibyl.sources.zuul.apis.ZuulAPI`
    :param kwargs: Arguments coming from the CLI.
    :return: List of retrieved tenants.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.TenantResponse`]
    """
    tenants = TenantsRequest(zuul)

    # Apply tenants filters
    if 'tenants' in kwargs:
        targets = kwargs['tenants'].value

        # An empty '--tenants' means all of them.
        if targets:
            tenants.with_name(*targets)
    else:
        # Check configuration file
        if 'defaults' in kwargs:
            defaults = kwargs['defaults']

            if 'tenants' in defaults:
                targets = defaults['tenants']

                # An empty 'tenants: ' means none of them.
                if not targets:
                    LOG.warning('No tenants selected for query. '
                                'Please check your configuration file.')

                tenants.with_name(*targets)

    return tenants.get()
