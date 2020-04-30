import json
import logging
from os import makedirs
from os.path import dirname, relpath
import aiofiles

from innoconv.utils import to_ast
from innoconv.workers.base import AbstractWorker


class ConvertAst(AbstractWorker):
    async def _task(self):
        while True:
            try:
                type, filepath, filepath_out = await self._input_q.get()
                rel_path = dirname(relpath(filepath, self._source_dir))
                logging.info("Job received: %s", filepath)

                self._notify_extensions("pre_process_file", rel_path)
                ast, title, short_title = await to_ast(filepath)
                self._notify_extensions("post_process_file", ast, title, type)

                await self._write_ast(filepath_out, ast)
                logging.info("Wrote %s", filepath_out)

                if type == "page":
                    # TODO: set short_title
                    try:
                        page["short_title"][language] = short_title
                    except KeyError:
                        page["short_title"] = {language: short_title}
                    page["title"][language] = title

            except Exception:
                logging.exception("Exception")
            finally:
                self.task_done()

    async def _write_ast(self, filepath_out, ast):
        makedirs(dirname(filepath_out), exist_ok=True)
        async with aiofiles.open(filepath_out, mode="w") as out_file:
            await out_file.write(json.dumps(ast))
            await out_file.flush()
