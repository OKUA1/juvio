import sys
import nbformat

if sys.version_info >= (3, 11):
    import tomllib
else:
    raise ImportError("Python 3.11+ is required for tomllib support.")


class JuvioConverter:
    @staticmethod
    def _parse_metadata(metadata_lines):
        toml_text = "\n".join(metadata_lines)
        data = tomllib.loads(toml_text)

        if "requires-python" in data:
            version = data["requires-python"]
            # Clean up operators like >=, ~=, etc.
            for prefix in (">=", "~=", "==", ">", "<=", "<"):
                if version.startswith(prefix):
                    version = version[len(prefix) :].strip()
                    break
            data["python_version"] = version
            data.pop("requires-python", None)
        return data

    @staticmethod
    def _generate_metadata(python_version, dependencies):
        lines = []
        lines.append(f'requires-python = "=={python_version}"')
        if dependencies:
            lines.append("dependencies = [")
            for dep in dependencies:
                lines.append(f'  "{dep}",')
            lines.append("]")
        else:
            lines.append("dependencies = []")
        return lines

    @staticmethod
    def convert_script_to_notebook(text: str):
        nb = nbformat.v4.new_notebook()
        nb.metadata.kernelspec = {
            "name": "juvio",
            "language": "python",
            "display_name": "Juvio",
        }
        nb.metadata.language_info = {
            "name": "python",
            "version": "3.10",
            "mimetype": "text/x-python",
            "codemirror_mode": {"name": "ipython", "version": 3},
            "pygments_lexer": "ipython3",
            "nbconvert_exporter": "python",
            "file_extension": ".py",
        }

        lines = text.splitlines()
        metadata_lines = []
        body_lines = []
        in_metadata = False

        for line in lines:
            if line.startswith("# ///"):
                in_metadata = not in_metadata
            elif in_metadata:
                if line.strip().startswith("#"):
                    metadata_lines.append(line.strip("# ").rstrip())
            else:
                body_lines.append(line)

        lines = body_lines
        cells = []
        cell_source = []
        cell_type = "code"

        for line in lines:
            if line.startswith("# %%"):
                if cell_source:
                    if cell_type == "markdown":
                        cleaned = [
                            l[2:] if l.startswith("# ") else l.lstrip("#")
                            for l in cell_source
                        ]
                        cells.append(nbformat.v4.new_markdown_cell("\n".join(cleaned)))
                    else:
                        cells.append(nbformat.v4.new_code_cell("\n".join(cell_source)))
                    cell_source = []

                if "markdown" in line.lower():
                    cell_type = "markdown"
                else:
                    cell_type = "code"
            else:
                cell_source.append(line)

        if cell_source:
            if cell_type == "markdown":
                cleaned = [
                    l[2:] if l.startswith("# ") else l.lstrip("#") for l in cell_source
                ]
                cells.append(nbformat.v4.new_markdown_cell("\n".join(cleaned)))
            else:
                cells.append(nbformat.v4.new_code_cell("\n".join(cell_source)))

        if not cells:
            cells.append(nbformat.v4.new_code_cell(""))

        nb.cells = cells
        return nb

    @staticmethod
    def convert_notebook_to_script(nb, dep_metadata: list[str] | None = None):
        dep_metadata = dep_metadata or []
        lines = []

        if dep_metadata:
            lines.append("# /// script")
            for line in dep_metadata:
                lines.append("# " + line)
            lines.append("# ///")

        for cell in nb.cells:
            if cell.cell_type == "code":
                lines.append("# %%")
                lines.append(cell.source.rstrip() if cell.source else "")
            elif cell.cell_type == "markdown":
                lines.append("# %% markdown")
                if cell.source:
                    for line in cell.source.rstrip().splitlines():
                        lines.append(
                            "# " + line if not line.startswith("#") else "# " + line
                        )
                else:
                    lines.append("")

        return "\n".join(lines) + "\n"

    @staticmethod
    def create(python_version="3.10", dependencies=None):
        if dependencies is None:
            dependencies = []

        lines = []
        lines.append("# /// script")
        metadata_block = JuvioConverter._generate_metadata(python_version, dependencies)
        for line in metadata_block:
            lines.append("# " + line)
        lines.append("# ///")
        lines.append("# %%")
        lines.append("")
        return "\n".join(lines) + "\n"

    @staticmethod
    def extract_metadata(text: str):
        lines = text.splitlines()
        metadata_lines = []
        in_metadata = False

        for line in lines:
            if line.startswith("# ///"):
                in_metadata = not in_metadata
            elif in_metadata:
                if line.strip().startswith("#"):
                    metadata_lines.append(line.strip("# ").rstrip())

        if metadata_lines:
            return JuvioConverter._parse_metadata(metadata_lines)
        else:
            return {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "dependencies": [],
            }
