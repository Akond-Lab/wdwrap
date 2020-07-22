#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from __future__ import annotations

from configparser import NoSectionError, NoOptionError
from typing import Callable, Mapping, Optional
import logging

from dask.distributed import Client, Future

from wdwrap.config import cfg
from wdwrap.runners import LcRunner

class JobScheduler(object):
    _instance: Optional[JobScheduler] = None

    def __init__(self,
                 executors: Optional[Mapping[str, Callable]] = None,
                 client: Optional[Client] = None,) -> None:
        if self._instance is not None:
            raise RuntimeError(
                'Do instance JobScheduler directly, use JobScheduler.instance to obtain singleton instance')
        super().__init__()
        if executors is None:
            executors = {}
        self.executors = executors
        if client is None:
            try:
                n = cfg().getint('jobs', 'workers')
            except (NoSectionError, NoOptionError, ValueError):
                n = None
            logging.info(f'Setting up multiprocess dash client with {n} workers')
            client = Client(n_workers=n)
        self.client = client

    def schedule(self, job_kind, *args, **kwargs) -> Future:
        ex = self.get_job_executor(job_kind)
        return self.client.submit(ex, *args, **kwargs)

    def get_job_executor(self, job_kind) -> Callable:
        return self.executors.get(job_kind, None)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = JobScheduler({
                'lc': LcRunner(),
            })
        return cls._instance
