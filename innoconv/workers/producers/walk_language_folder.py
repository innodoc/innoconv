import json
import logging
from os.path import abspath, dirname, exists, isdir, join, relpath
from os import makedirs, walk
import pathlib

import aiofiles

from innoconv.workers.base import AbstractWorker
from innoconv.constants import CONTENT_BASENAME, FOOTER_FRAGMENT_PREFIX, PAGES_FOLDER
from innoconv.utils import to_ast


class WalkLanguageFolder(AbstractWorker):
    def __init__(self, languages, source_dir, output_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._languages = languages
        self._sections = []
        self._source_dir = source_dir
        self._output_dir = output_dir

    async def get_total(self):
        return len(self._torrent_ids)

    async def _task(self):
        # self._notify_extensions("start", self._output_dir, self._source_dir)
        for i, language in enumerate(self._languages):
            # self._notify_extensions("pre_conversion", language)
            logging.info("Processing language %s", language)
            await self._convert_language_folder(language, i)
            # self._notify_extensions("post_conversion", language)
        # self._notify_extensions("finish")

    async def _convert_language_folder(self, language, lang_num):
        path = abspath(join(self._source_dir, language))

        if not isdir(path):
            raise RuntimeError("Error: Directory {} does not exist".format(path))

        section_num = 0
        for root, dirs, files in walk(path):
            rel_path = relpath(root, path)

            # skip meta directories like '_static'
            parts = pathlib.Path(rel_path).parts
            if parts and parts[0].startswith("_"):
                continue

            # note: all dirs manipulation must happen in-place!
            dirs.sort()  # sort section names

            # process section
            content_filename = "{}.md".format(CONTENT_BASENAME)
            if content_filename in files:
                filepath = join(root, content_filename)
                await self._process_section(filepath, lang_num, section_num)
                section_num += 1
            else:
                raise RuntimeError(
                    "Found section without content file: {}".format(root)
                )

        if section_num != len(self._sections):
            raise RuntimeError(
                "Inconsistent directory structure: "
                "Language {} is missing sections.".format(language)
            )

        # process pages
        try:
            pages = self._manifest.pages
        except AttributeError:
            pages = []
        for page in pages:
            await self._process_page(page, language)

        await self._process_footer_fragments(language)

    async def _process_section(self, filepath, lang_num, section_num):
        logging.info("Processing section file %s", filepath)
        rel_path = dirname(relpath(filepath, self._source_dir))
        section_name = rel_path[3:]  # strip language
        if lang_num == 0:
            # record sections for first language
            self._sections.append(section_name)
        else:
            # ensure sections are identical for all languages
            try:
                if self._sections[section_num] != section_name:
                    raise RuntimeError(
                        "Inconsistent directory structure: "
                        "Section {} differs.".format(rel_path)
                    )
            except IndexError:
                raise RuntimeError(
                    "Inconsistent directory structure: "
                    "Extra section {} present.".format(rel_path)
                )

        # self._notify_extensions("pre_process_file", rel_path)
        ast, title, _ = await to_ast(filepath)
        # self._notify_extensions("post_process_file", ast, title, "section")

        output_filename = "{}.json".format(CONTENT_BASENAME)
        filepath_out = join(self._output_dir, rel_path, output_filename)
        await self._write_ast(filepath_out, ast)
        logging.info("Wrote %s", filepath_out)

    async def _process_page(self, page, language):
        try:
            link_in_nav = page["link_in_nav"]
        except KeyError:
            link_in_nav = False
        try:
            link_in_footer = page["link_in_footer"]
        except KeyError:
            link_in_footer = False
        if not (link_in_nav or link_in_footer):
            logging.warning(
                "Page '%s' should have at least on of "
                "link_in_nav or link_in_nav set to true."
            )
            return
        try:
            page["title"]
        except KeyError:
            page["title"] = {}
        input_filename = "{}.md".format(page["id"])
        filepath = join(self._source_dir, language, PAGES_FOLDER, input_filename)
        rel_path = dirname(relpath(filepath, self._source_dir))

        # convert
        # self._notify_extensions("pre_process_file", rel_path)
        ast, title, short_title = await to_ast(filepath)
        # self._notify_extensions("post_process_file", ast, title, "page")
        try:
            page["short_title"][language] = short_title
        except KeyError:
            page["short_title"] = {language: short_title}
        page["title"][language] = title

        # write json output
        output_filename = "{}.json".format(page["id"])
        filepath_out = join(self._output_dir, rel_path, output_filename)
        await self._write_ast(filepath_out, ast)
        logging.info("Wrote %s", filepath_out)

    async def _process_footer_fragments(self, language):
        for part in ("a", "b"):
            input_filename = "{}{}.md".format(FOOTER_FRAGMENT_PREFIX, part)
            filepath = join(self._source_dir, language, input_filename)
            rel_path = dirname(relpath(filepath, self._source_dir))
            if not exists(filepath):
                logging.warning("Footer fragment %s does not exist.", filepath)
                continue

            # convert
            # self._notify_extensions("pre_process_file", rel_path)
            ast, title, _ = await to_ast(filepath, ignore_missing_title=True)
            # self._notify_extensions("post_process_file", ast, title, "fragment")

            # write json output
            output_filename = "{}{}.json".format(FOOTER_FRAGMENT_PREFIX, part)
            filepath_out = join(self._output_dir, rel_path, output_filename)
            await self._write_ast(filepath_out, ast)
            logging.info("Wrote %s", filepath_out)

    async def _write_ast(self, filepath_out, ast):
        makedirs(dirname(filepath_out), exist_ok=True)
        async with aiofiles.open(filepath_out, mode="w") as out_file:
            await out_file.write(json.dumps(ast))
            await out_file.flush()
