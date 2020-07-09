#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from __future__ import annotations
from typing import Callable, Mapping, Optional
import logging

from dask.distributed import Client, Future
from wdwrap.runners import LcRunner

class JobScheduler(object):
    _instance: Optional[JobScheduler] = None

    def __init__(self,
                 executors: Optional[Mapping[str, Callable]] = None,
                 client: Optional[Client] = None) -> None:
        if self._instance is not None:
            raise RuntimeError(
                'Do instance JobScheduler directly, use JobScheduler.instance to obtain singleton instance')
        super().__init__()
        if executors is None:
            executors = {}
        self.executors = executors
        if client is None:
            logging.info('Setting up multiprocess dash client')
            client = Client()
        self.client = client

    def schedule(self, job_kind, *args) -> Future:
        ex = self.get_job_executor(job_kind)
        return self.client.submit(ex, *args)

    def get_job_executor(self, job_kind) -> Callable:
        return self.executors.get(job_kind, None)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = JobScheduler({
                'lc': LcRunner(),
            })
        return cls._instance
