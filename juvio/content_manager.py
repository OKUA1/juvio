import nbformat
import inspect
import aiofiles
from juvio.converter import JuvioConverter
from juvio.shared import FileLock, AsyncFileLock
import os


def _is_juvio_file(path):
    return path.endswith(".juvio")


def juvio_get_sync(self, path, content=True, type=None, format=None, **kwargs):
    api_path = path.replace("\\", "/").lstrip("/")
    full_path = self._get_os_path(api_path)

    if not _is_juvio_file(api_path):
        return self._original_get(
            api_path, content=content, type=type, format=format, **kwargs
        )

    model = self._original_get(api_path, content=False, **kwargs)

    if not content:
        model["type"] = "notebook"
        return model

    try:
        with FileLock(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                text = f.read()
        nb = JuvioConverter.convert_script_to_notebook(text)
        nbformat.validate(nb)
        model.update(type="notebook", format="json", content=nb)
        return model
    except Exception as e:
        from tornado.web import HTTPError

        raise HTTPError(500, f"Error while reading {api_path}: {e}")


def juvio_save_sync(self, model, path, **kwargs):
    from datetime import datetime

    def format_timestamp(timestamp):
        return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    model_type = model.get("type")
    model_content = model.get("content")

    api_path = path.replace("\\", "/").lstrip("/")
    full_path = self._get_os_path(api_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if not _is_juvio_file(api_path) or model_type != "notebook":
        return self._original_save(model, api_path, **kwargs)

    try:
        with FileLock(full_path):
            pass  # ensures lock before opening

        if model_content is not None:
            if isinstance(model_content, dict):
                nb = nbformat.from_dict(model_content)
            else:
                nb = model_content

            nbformat.validate(nb)
            with open(full_path, "r", encoding="utf-8") as f:
                existing = f.read()

            metadata = JuvioConverter._generate_metadata(
                **JuvioConverter.extract_metadata(existing)
            )
            text = JuvioConverter.convert_notebook_to_script(nb, metadata)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(JuvioConverter.create())

        stat = os.stat(full_path)

        return {
            "name": os.path.basename(api_path),
            "path": api_path,
            "type": "notebook",
            "format": None,
            "content": None,
            "created": format_timestamp(stat.st_ctime),
            "last_modified": format_timestamp(stat.st_mtime),
            "writable": True,
            "mimetype": None,
        }
    except Exception as e:
        from tornado.web import HTTPError

        raise HTTPError(500, f"Error while saving {api_path}: {e}")


async def juvio_get_async(self, path, content=True, type=None, format=None, **kwargs):
    api_path = path.replace("\\", "/").lstrip("/")
    full_path = self._get_os_path(api_path)

    if not _is_juvio_file(api_path):
        return await self._original_get(
            api_path, content=content, type=type, format=format, **kwargs
        )

    model = await self._original_get(api_path, content=False, **kwargs)

    if not content:
        model["type"] = "notebook"
        return model

    try:
        async with AsyncFileLock(full_path):
            pass  # ensures lock before opening

        async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
            text = await f.read()

        nb = JuvioConverter.convert_script_to_notebook(text)
        nbformat.validate(nb)
        model.update(type="notebook", format="json", content=nb)
        return model
    except Exception as e:
        from tornado.web import HTTPError

        raise HTTPError(500, f"Error while reading {api_path}: {e}")


async def juvio_save_async(self, model, path, **kwargs):
    from datetime import datetime

    def format_timestamp(timestamp):
        return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    model_type = model.get("type")
    model_content = model.get("content")

    api_path = path.replace("\\", "/").lstrip("/")
    full_path = self._get_os_path(api_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if not _is_juvio_file(api_path) or model_type != "notebook":
        return await self._original_save(model, api_path, **kwargs)

    try:
        async with AsyncFileLock(full_path):
            pass  # ensures lock before opening

        if model_content is not None:
            if isinstance(model_content, dict):
                nb = nbformat.from_dict(model_content)
            else:
                nb = model_content

            nbformat.validate(nb)
            async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
                existing = await f.read()

            metadata = JuvioConverter._generate_metadata(
                **JuvioConverter.extract_metadata(existing)
            )
            text = JuvioConverter.convert_notebook_to_script(nb, metadata)

            async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
                await f.write(text)
        else:
            async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
                await f.write(JuvioConverter.create())

        stat = os.stat(full_path)

        return {
            "name": os.path.basename(api_path),
            "path": api_path,
            "type": "notebook",
            "format": None,
            "content": None,
            "created": format_timestamp(stat.st_ctime),
            "last_modified": format_timestamp(stat.st_mtime),
            "writable": True,
            "mimetype": None,
        }
    except Exception as e:
        from tornado.web import HTTPError

        raise HTTPError(500, f"Error while saving {api_path}: {e}")


def juvio_rename_file(self, old_path, new_path):
    old_api_path = old_path.replace("\\", "/").lstrip("/")
    new_api_path = new_path.replace("\\", "/").lstrip("/")
    full_path = self._get_os_path(new_api_path)

    result = self._original_rename_file(old_api_path, new_api_path)

    if _is_juvio_file(new_api_path):
        with FileLock(full_path):
            if os.path.getsize(full_path) == 0:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(JuvioConverter.create())

    return result


async def rename_file(self, old_path, new_path):
    old_api_path = old_path.replace("\\", "/").lstrip("/")
    new_api_path = new_path.replace("\\", "/").lstrip("/")
    full_path = self._get_os_path(new_api_path)

    result = await self._original_rename_file(old_api_path, new_api_path)

    async with AsyncFileLock(full_path):
        if os.path.getsize(full_path) == 0:
            async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
                await f.write(JuvioConverter.create())

    return result


def create_juvio_contents_manager_class(base_manager_class):
    is_async = inspect.iscoroutinefunction(base_manager_class.get)
    if is_async:

        class AsyncJuvioContentsManager(base_manager_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._original_get = super().get
                self._original_save = super().save
                self._original_rename_file = super().rename_file

            async def get(self, path, content=True, type=None, format=None, **kwargs):
                return await juvio_get_async(
                    self, path, content=content, type=type, format=format, **kwargs
                )

            async def save(self, model, path, **kwargs):
                return await juvio_save_async(self, model, path, **kwargs)

            async def rename_file(self, old_path, new_path):
                return await rename_file(self, old_path, new_path)

        return AsyncJuvioContentsManager

    else:

        class JuvioContentsManager(base_manager_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._original_get = super().get
                self._original_save = super().save
                self._original_rename_file = super().rename_file

            def get(self, path, content=True, type=None, format=None, **kwargs):
                return juvio_get_sync(
                    self, path, content=content, type=type, format=format, **kwargs
                )

            def save(self, model, path, **kwargs):
                return juvio_save_sync(self, model, path, **kwargs)

            def rename_file(self, old_path, new_path):
                return juvio_rename_file(self, old_path, new_path)

        return JuvioContentsManager
