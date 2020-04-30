import asyncio
import logging
import signal

from innoconv.constants import CPU_COUNT
from innoconv.ext import EXTENSIONS
from innoconv.workers.consumers.convert_ast import ConvertAst
from innoconv.workers.producers.walk_language_folder import WalkLanguageFolder

CONSUMERS = (
    (ConvertAst, CPU_COUNT, 0),
    # (ConvertAst, 2, 0),
    # (ConvertAst, 1, 0),
)


class Supervisor(object):
    def __init__(self, source_dir, output_dir, manifest, extensions):
        self._source_dir = source_dir
        self._output_dir = output_dir
        self._manifest = manifest
        self._extensions = []
        self._load_extensions(extensions)
        self._consumers = []

    def start(self):
        self._loop = asyncio.get_event_loop()
        # handle signals
        for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
            self._loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(self._handle_signal(s))
            )
        # start async work
        try:
            self._loop.run_until_complete(self._run())
            logging.info("Finished")
        except asyncio.CancelledError:
            logging.info("Cancelled")
            raise
        finally:
            self._loop.run_until_complete(self._cleanup())
            self._loop.stop()

    async def _run(self):
        logging.info(f"Starting (using {CPU_COUNT} cores)")
        await self._create_workers()
        await self._wait_for_workers()

    async def _create_workers(self):
        self._producer = WalkLanguageFolder(
            self._manifest.languages,
            self._source_dir,
            self._output_dir,
            output_q_size=128
        )
        # self._manifest.languages, output_q_size=Q_SIZE_LANGUAGE_FOLDER)

        # consumer chain
        for i, (Worker, num_workers, output_q_size) in enumerate(CONSUMERS):
            # prev_worker = self._producer if i == 0 else self._consumers[-1][0]
            prev_worker = self._producer
            workers = []
            for _ in range(num_workers):
                worker = Worker(prev_worker.output_q, output_q_size=output_q_size)
                workers.append(worker)
            self._consumers.append(workers)

        # progress bars
        # if not self._disable_progress_bar:
        #     self._worker_progress_bars = ProgressBars(self._producer, self._consumers)

    async def _wait_for_workers(self):
        await self._producer.get_task()
        # wait for all items to be processed
        for worker in [workers[0] for workers in self._consumers]:
            await worker.input_q.join()
        # cancel workers
        for workers in self._consumers:
            for worker in workers:
                worker.get_task().cancel()

    async def _cleanup(self):
        workers = [w[0] for w in self._consumers]
        if self._producer is not None:
            workers.append(self._producer)
        for worker in workers:
            Worker = type(worker)
            await Worker.cleanup()
            logging.debug("Cleaned up %s", Worker.__name__)
        # await asyncio.sleep(0.25)  # give aiohttp time to close TLS connections
        logging.info("Shutdown complete")

    async def _shutdown(self):
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _handle_signal(self, s):
        logging.info(f"Received {s.name}. Shutting down...")
        await self._shutdown()

    def _notify_extensions(self, event_name, *args, **kwargs):
        for ext in self._extensions:
            func = getattr(ext, event_name)
            func(*args, **kwargs)

    def _load_extensions(self, extensions):
        for ext_name in extensions:
            try:
                self._extensions.append(EXTENSIONS[ext_name](self._manifest))
            except (ImportError, KeyError) as exc:
                raise RuntimeError("Extension {} not found!".format(ext_name)) from exc
        # pass extension list to extenions
        self._notify_extensions("extension_list", self._extensions)
