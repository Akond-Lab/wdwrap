#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from __future__ import annotations
from typing import Callable, Mapping, Optional

from dask.distributed import Client, Future
from wdwrap.runners import LcRunner

class JobScheduler(object):
    instance: Optional[JobScheduler] = None

    def __init__(self,
                 executors: Optional[Mapping[str, Callable]] = None,
                 client: Optional[Client] = None) -> None:
        if self.instance is not None:
            raise RuntimeError(
                'Do instance JobScheduler directly, use JobScheduler.instance to obtain singleton instance')
        super().__init__()
        if executors is None:
            executors = {}
        self.executors = executors
        if client is None:
            client = Client()
        self.client = client

    def schedule(self, job_kind, *args) -> Future:
        ex = self.get_job_executor(job_kind)
        return self.client.submit(ex, *args)

    def get_job_executor(self, job_kind) -> Callable:
        return self.executors.get(job_kind, None)


JobScheduler.instance = JobScheduler({'lc': LcRunner()})
