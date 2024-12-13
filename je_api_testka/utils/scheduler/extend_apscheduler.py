from datetime import datetime
from typing import Callable, Any, Union

from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.util import undefined

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


class SchedulerManager(object):

    def __init__(self):
        apitestka_logger.info("Init SchedulerManager")
        self._blocking_schedulers: BlockingScheduler = BlockingScheduler()
        self._background_schedulers: BackgroundScheduler = BackgroundScheduler()
        self.blocking_scheduler_event_dict = {
            "secondly": self.add_interval_blocking_secondly,
            "minutely": self.add_interval_blocking_minutely,
            "hourly": self.add_interval_blocking_hourly,
            "daily": self.add_interval_blocking_daily,
            "weekly": self.add_interval_blocking_weekly,
        }
        self.nonblocking_scheduler_event_dict = {
            "secondly": self.add_interval_nonblocking_secondly,
            "minutely": self.add_interval_nonblocking_minutely,
            "hourly": self.add_interval_nonblocking_hourly,
            "daily": self.add_interval_nonblocking_daily,
            "weekly": self.add_interval_nonblocking_weekly,
        }

    def add_blocking_job(
            self, func: Callable, trigger: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, id: str = None, name: str = None,
            misfire_grace_time: int = undefined, coalesce: bool = undefined, max_instances: int = undefined,
            next_run_time: datetime = undefined, jobstore: str = 'default', executor: str = 'default',
            replace_existing: bool = False, **trigger_args: Any) -> Job:
        """
        Just an apscheduler add job wrapper.
        :param func: callable (or a textual reference to one) to run at the given time
        :param str|apscheduler.triggers.base.BaseTrigger trigger: trigger that determines when
            ``func`` is called
        :param list|tuple args: list of positional arguments to call func with
        :param dict kwargs: dict of keyword arguments to call func with
        :param str|unicode id: explicit identifier for the job (for modifying it later)
        :param str|unicode name: textual description of the job
        :param int misfire_grace_time: seconds after the designated runtime that the job is still
            allowed to be run (or ``None`` to allow the job to run no matter how late it is)
        :param bool coalesce: run once instead of many times if the scheduler determines that the
            job should be run more than once in succession
        :param int max_instances: maximum number of concurrently running instances allowed for this
            job
        :param datetime next_run_time: when to first run the job, regardless of the trigger (pass
            ``None`` to add the job as paused)
        :param str|unicode jobstore: alias of the job store to store the job in
        :param str|unicode executor: alias of the executor to run the job with
        :param bool replace_existing: ``True`` to replace an existing job with the same ``id``
            (but retain the number of runs from the existing one)
        :return: Job
        """
        apitestka_logger.info("SchedulerManager add_blocking_job "
                              f"func: {func} "
                              f"trigger: {trigger} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"id: {id} "
                              f"name: {name} "
                              f"misfire_grace_time: {misfire_grace_time} "
                              f"coalesce: {coalesce} "
                              f"max_instances: {max_instances} "
                              f"next_run_time: {next_run_time} "
                              f"jobstore: {jobstore} "
                              f"executor: {executor} "
                              f"replace_existing: {replace_existing} "
                              f"trigger_args: {trigger_args}")
        params = locals()
        params.pop("self")
        params.pop("trigger_args")
        return self._blocking_schedulers.add_job(**params, **trigger_args)

    def add_nonblocking_job(
            self, func: Callable, trigger: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, id: str = None, name: str = None,
            misfire_grace_time: int = undefined, coalesce: bool = undefined, max_instances: int = undefined,
            next_run_time: datetime = undefined, jobstore: str = 'default', executor: str = 'default',
            replace_existing: bool = False, **trigger_args: Any) -> Job:
        """
        Just an apscheduler add job wrapper.
        :param func: callable (or a textual reference to one) to run at the given time
        :param str|apscheduler.triggers.base.BaseTrigger trigger: trigger that determines when
            ``func`` is called
        :param list|tuple args: list of positional arguments to call func with
        :param dict kwargs: dict of keyword arguments to call func with
        :param str|unicode id: explicit identifier for the job (for modifying it later)
        :param str|unicode name: textual description of the job
        :param int misfire_grace_time: seconds after the designated runtime that the job is still
            allowed to be run (or ``None`` to allow the job to run no matter how late it is)
        :param bool coalesce: run once instead of many times if the scheduler determines that the
            job should be run more than once in succession
        :param int max_instances: maximum number of concurrently running instances allowed for this
            job
        :param datetime next_run_time: when to first run the job, regardless of the trigger (pass
            ``None`` to add the job as paused)
        :param str|unicode jobstore: alias of the job store to store the job in
        :param str|unicode executor: alias of the executor to run the job with
        :param bool replace_existing: ``True`` to replace an existing job with the same ``id``
            (but retain the number of runs from the existing one)
        :return: Job
        """
        apitestka_logger.info("SchedulerManager add_nonblocking_job "
                              f"func: {func} "
                              f"trigger: {trigger} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"id: {id} "
                              f"name: {name} "
                              f"misfire_grace_time: {misfire_grace_time} "
                              f"coalesce: {coalesce} "
                              f"max_instances: {max_instances} "
                              f"next_run_time: {next_run_time} "
                              f"jobstore: {jobstore} "
                              f"executor: {executor} "
                              f"replace_existing: {replace_existing} "
                              f"trigger_args: {trigger_args}")
        params = locals()
        params.pop("self")
        params.pop("trigger_args")
        return self._blocking_schedulers.add_job(**params, **trigger_args)

    def get_blocking_scheduler(self) -> BlockingScheduler:
        """
        Return self blocking scheduler
        :return: BlockingScheduler
        """
        apitestka_logger.info("SchedulerManager get_blocking_scheduler")
        return self._blocking_schedulers

    def get_nonblocking_scheduler(self) -> BackgroundScheduler:
        """
        Return self background scheduler
        :return: BackgroundScheduler
        """
        apitestka_logger.info("SchedulerManager get_nonblocking_scheduler")
        return self._background_schedulers

    def start_block_scheduler(self, *args: Any, **kwargs: Any) -> None:
        """
        Start blocking scheduler
        :return: None
        """
        apitestka_logger.info(f"SchedulerManager start_block_scheduler args: {args} kwargs: {kwargs}")
        self._blocking_schedulers.start(*args, **kwargs)

    def start_nonblocking_scheduler(self, *args: Any, **kwargs: Any) -> None:
        """
        Start background scheduler
        :return: None
        """
        apitestka_logger.info(f"SchedulerManager start_nonblocking_scheduler args: {args} kwargs: {kwargs}")
        self._background_schedulers.start(*args, **kwargs)

    def start_all_scheduler(self, *args: Any, **kwargs: Any) -> None:
        """
        Start background and blocking scheduler
        :return: None
        """
        apitestka_logger.info(f"SchedulerManager start_all_scheduler args: {args} kwargs: {kwargs}")
        self._blocking_schedulers.start(*args, **kwargs)
        self._background_schedulers.start(*args, **kwargs)

    def add_interval_blocking_secondly(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, seconds: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_blocking_secondly "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"seconds: {seconds} "
                              f"trigger_args: {trigger_args}")
        return self.add_blocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, seconds=seconds, **trigger_args)

    def add_interval_blocking_minutely(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, minutes: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_blocking_minutely "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"minutes: {minutes} "
                              f"trigger_args: {trigger_args}")
        return self.add_blocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, minutes=minutes, **trigger_args)

    def add_interval_blocking_hourly(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, hours: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_blocking_hourly "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"hours: {hours} "
                              f"trigger_args: {trigger_args}")
        return self.add_blocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, hours=hours, **trigger_args)

    def add_interval_blocking_daily(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, days: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_blocking_daily "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"days: {days} "
                              f"trigger_args: {trigger_args}")
        return self.add_blocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, days=days, **trigger_args)

    def add_interval_blocking_weekly(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, weeks: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_blocking_weekly "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"weeks: {weeks} "
                              f"trigger_args: {trigger_args}")
        return self.add_blocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, weeks=weeks, **trigger_args)

    def add_interval_nonblocking_secondly(
            self, function: Callable, id: str = None, args: list = None,
            kwargs: dict = None, seconds: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_nonblocking_secondly "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"seconds: {seconds} "
                              f"trigger_args: {trigger_args}")
        return self.add_nonblocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, seconds=seconds, **trigger_args)

    def add_interval_nonblocking_minutely(
            self, function: Callable, id: str = None, args: list = None,
            kwargs: dict = None, minutes: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_nonblocking_minutely "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"minutes: {minutes} "
                              f"trigger_args: {trigger_args}")
        return self.add_nonblocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, minutes=minutes, **trigger_args)

    def add_interval_nonblocking_hourly(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, hours: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_nonblocking_hourly "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"hours: {hours} "
                              f"trigger_args: {trigger_args}")
        return self.add_nonblocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, hours=hours, **trigger_args)

    def add_interval_nonblocking_daily(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, days: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_nonblocking_daily "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"days: {days} "
                              f"trigger_args: {trigger_args}")
        return self.add_nonblocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, days=days, **trigger_args)

    def add_interval_nonblocking_weekly(
            self, function: Callable, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, weeks: int = 1, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_interval_nonblocking_weekly "
                              f"function: {function} "
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"weeks: {weeks} "
                              f"trigger_args: {trigger_args}")
        return self.add_nonblocking_job(
            func=function, trigger="interval", id=id, args=args, kwargs=kwargs, weeks=weeks, **trigger_args)

    def add_cron_blocking(
            self, function: Callable, id: str = None, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_cron_blocking "
                              f"function: {function} "
                              f"id: {id} "
                              f"trigger_args: {trigger_args}")
        return self.add_blocking_job(func=function, id=id, trigger="cron", **trigger_args)

    def add_cron_nonblocking(
            self, function: Callable, id: str = None, **trigger_args: Any) -> Job:
        apitestka_logger.info("SchedulerManager add_cron_nonblocking "
                              f"function: {function} "
                              f"id: {id} "
                              f"trigger_args: {trigger_args}")
        return self.add_nonblocking_job(func=function, id=id, trigger="cron", **trigger_args)

    def remove_blocking_job(self, id: str, jobstore: str = 'default') -> Any:
        apitestka_logger.info("SchedulerManager remove_blocking_job "
                              f"id: {id} "
                              f"jobstore: {jobstore}")
        return self._blocking_schedulers.remove_job(job_id=id, jobstore=jobstore)

    def remove_nonblocking_job(self, id: str, jobstore: str = 'default') -> Any:
        apitestka_logger.info("SchedulerManager remove_nonblocking_job "
                              f"id: {id} "
                              f"jobstore: {jobstore}")
        return self._background_schedulers.remove_job(job_id=id, jobstore=jobstore)

    def shutdown_blocking_scheduler(self, wait: bool = False) -> None:
        apitestka_logger.info(f"SchedulerManager shutdown_blocking_scheduler wait: {wait}")
        self._blocking_schedulers.shutdown(wait=wait)

    def shutdown_nonblocking_scheduler(self, wait: bool = False) -> None:
        apitestka_logger.info(f"SchedulerManager shutdown_nonblocking_scheduler wait: {wait}")
        self._background_schedulers.shutdown(wait=wait)


scheduler_manager = SchedulerManager()
