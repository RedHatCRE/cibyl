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


def perform_variants_query(job, **kwargs):
    """Query for variants.

    :param job: API to interact with the owner of the variants.
    :type job: :class:`cibyl.sources.zuul.transactions.JobResponse`
    :param kwargs: Arguments coming from the CLI.
    :return: List of retrieved variants.
    :rtype: list[:class:`cibyl.sources.zuul.transactions.VariantResponse`]
    """
    return job.variants().get()
