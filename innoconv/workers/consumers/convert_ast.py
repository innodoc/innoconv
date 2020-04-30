import json
import logging
from os import makedirs
from os.path import dirname
import aiofiles

from innoconv.utils import to_ast
from innoconv.workers.base import AbstractWorker


class ConvertAst(AbstractWorker):
    async def _task(self):
        while True:
            try:
                filepath, filepath_out = await self._input_q.get()
                logging.info("Job received: %s", filepath)

                # self._notify_extensions("pre_process_file", rel_path)
                ast, title, _ = await to_ast(filepath)
                # self._notify_extensions("post_process_file", ast, title, "section")

                # write file content
                makedirs(dirname(filepath_out), exist_ok=True)
                async with aiofiles.open(filepath_out, mode="w") as out_file:
                    await out_file.write(json.dumps(ast))
                    await out_file.flush()
                logging.info("Wrote %s", filepath_out)
            except Exception:
                logging.exception("Exception")
            finally:
                self.task_done()
