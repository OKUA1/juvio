<div align="center">
  <img alt="logo" src="https://gist.githubusercontent.com/OKUA1/d6e65e883546021ea774857878fd0537/raw/4de2ea217e25d9ff7b3d2a73899e85665ed7d94c/juvio_logo.svg" height = "250">
</div>


# **Juvio**: reproducible, dependency-aware, and Git-friendly Jupyter Notebooks.

## 🚀 What It Does

- 💡 **Inline Dependency Management**

  Install packages right from the notebook:

  ```python
  %juvio install numpy pandas
  ```

  Dependencies are saved directly in the notebook as metadata (PEP 723-style), like:
  ```python
  # /// script
  # requires-python = "==3.10.17"
  # dependencies = [
  # "numpy==2.2.5",
  # "pandas==2.2.3"
  # ]
  # ///
  ```

- ⚙️ **Automatic Environment Setup**

    When the notebook is opened, Juvio installs the dependencies automatically in an ephemeral virtual environment (using `uv`), ensuring that the notebook runs with the correct versions of the packages and Python.

- 📁 **Git-Friendly Format**

    Notebooks are converted on the fly to a script-style format using `# %%` markers, making diffs and version control painless:
    ```python
    # %%
    %juvio install numpy
    # %%
    import numpy as np
    # %%
    arr = np.array([1, 2, 3])
    print(arr)
    # %%
    ```

## 🧑‍💻 How to Use

**1. Install Juvio:**

```bash
pip install juvio
jupyter labextension enable juvio-frontend
```

**2. Make sure you have uv installed:**

https://docs.astral.sh/uv/getting-started/installation/

**3. Start JupyterLab and create a Juvio Notebook.**
 
**4. Install necessary packages in the notebook and run your code**

```python
  %juvio install ...
  ```
Dependencies are tracked, environments are reproducible, and your notebook stays Git-clean ✨

## Why Use Juvio?

- No additional lock or requirements files are needed
- Guaranteed reproducibility
- Cleaner Git diffs

## Powered By

- `uv` – ultra-fast Python package management
- `PEP 723` – Python inline dependency standards
- `jupytext`-like format for easy version control

