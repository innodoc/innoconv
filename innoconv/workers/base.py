import asyncio


class AbstractWorker(object):
    def __init__(
        self,
        manifest,
        source_dir,
        output_dir,
        extensions,
        input_q=None,
        output_q_size=0
    ):
        self._manifest = manifest
        self._source_dir = source_dir
        self._output_dir = output_dir
        self._extensions = extensions
        self._input_q = input_q
        if output_q_size > 0:
            self._output_q = asyncio.Queue(output_q_size)
        self._task = asyncio.create_task(self._task())
        self._tasks_done = 0

    @classmethod
    async def cleanup(cls):
        pass

    def get_task(self):
        return self._task

    def task_done(self):
        self._input_q.task_done()
        self._tasks_done += 1

    @property
    def tasks_done(self):
        return self._tasks_done

    @property
    def input_q(self):
        return self._input_q

    @property
    def output_q(self):
        return self._output_q

    async def _task(self):
        raise NotImplementedError()

    def _notify_extensions(self, event_name, *args, **kwargs):
        for ext in self._extensions:
            func = getattr(ext, event_name)
            func(*args, **kwargs)
