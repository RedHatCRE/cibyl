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
from overrides import overrides

from cibyl.sources.zuul.queries.composition import AggregatedQuery
from cibyl.sources.zuul.queries.composition.quick import QuickQuery
from cibyl.sources.zuul.queries.jobs import perform_jobs_query
from cibyl.sources.zuul.queries.pipelines import perform_pipelines_query
from cibyl.sources.zuul.transactions import PipelineResponse as Pipeline


class VerboseQuery(QuickQuery):
    """A kind of complex query that focuses on completeness over speed.
    """

    @overrides
    def with_jobs_query(self, **kwargs) -> 'AggregatedQuery':
        def is_job_in(pl: Pipeline) -> bool:
            return job.name in [jb.name for jb in pl.jobs().get()]

        # Cache pipelines for later use
        pipelines = perform_pipelines_query(self.api, **kwargs)

        for job in perform_jobs_query(self.api, **kwargs):
            model = self.tools.builder.with_job(job)

            # Include also pipelines where the job is present
            for pipeline in pipelines:
                if not is_job_in(pipeline):
                    continue

                # Register job as a child of the pipeline
                self.tools.builder.with_pipeline(pipeline).add_job(model)

        return self
