import os
import sys
import platform
from juvio.converter import JuvioConverter


current_path = os.path.dirname(os.path.abspath(__file__))

shared_path = os.path.join(current_path, "shared.py")


def cmd(
    python_version=None,
    deps=None,
):
    head = [
        "uv",
        "run",
        "--no-project",
        "--isolated",
        "--exact",
        "--with",
        "ipykernel",
    ]

    head.append("--python")
    if python_version is not None:
        head.append(python_version)
    else:
        head.append(f"{sys.version_info.major}.{sys.version_info.minor}")
    if deps is not None and len(deps) > 0:
        for dep in deps:
            head.append("--with")
            head.append(f"{dep}")
    else:
        head.append("-n")

    head.extend(["--", "python", shared_path])

    head += sys.argv[1:]
    return head


def main():
    notebook_path = os.environ.get("JPY_SESSION_NAME", None)

    if notebook_path is None:
        print("No notebook path found in environment variable JPY_SESSION_NAME.")
        sys.exit(1)

    with open(notebook_path, "r", encoding="utf-8") as f:
        text = f.read()

    metadata = JuvioConverter.extract_metadata(text)

    if platform.system() == "Windows":
        import subprocess

        proc = subprocess.Popen(
            cmd(
                python_version=metadata.get("python_version", None),
                deps=metadata.get("dependencies", []),
            )
        )
        proc.wait()
        sys.exit(proc.returncode)
    else:
        os.execvp(
            "uv",
            cmd(
                python_version=metadata.get("python_version", None),
                deps=metadata.get("dependencies", []),
            ),
        )
