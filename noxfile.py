"""
Automated testing via nox (https://nox.thea.codes/).

Combined with a working installation of nox (``pip install nox``), this file specifies a
matrix of tests, linters, and other quality checks which can be run individually or as a
suite.

To see available tasks, run ``nox --list``. To run all available tasks -- which requires
a functioning installation of at least one supported Python version -- run ``nox``. To
run a single task, use ``nox -s`` with the name of that task.

"""
import os
import pathlib
import shutil
import typing

import nox

nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True

PACKAGE_NAME = "django_registration"

NOXFILE_PATH = pathlib.Path(__file__).parents[0]
ARTIFACT_PATHS = (
    NOXFILE_PATH / "src" / f"{PACKAGE_NAME}.egg-info",
    NOXFILE_PATH / "build",
    NOXFILE_PATH / "dist",
    NOXFILE_PATH / "__pycache__",
    NOXFILE_PATH / "src" / "__pycache__",
    NOXFILE_PATH / "src" / PACKAGE_NAME / "__pycache__",
    NOXFILE_PATH / "tests" / "__pycache__",
)


def clean(paths: typing.Iterable[os.PathLike] = ARTIFACT_PATHS) -> None:
    """
    Clean up after a test run.

    """
    [
        shutil.rmtree(path) if path.is_dir() else path.unlink()
        for path in paths
        if path.exists()
    ]


# Tasks which run the package's test suites.
# -----------------------------------------------------------------------------------


@nox.session(tags=["tests"])
@nox.parametrize(
    "python,django",
    [
        # Python/Django testing matrix. Tests Django 3.2, 4.0, 4.1,
        # 4.2, on Python 3.7 through 3.11, skipping unsupported
        # combinations: Django 3.2 and 4.0 do not support Python 3.11,
        # and Django 4.0 and 4.1 do not support Python 3.7.
        (python, django)
        for python in ["3.7", "3.8", "3.9", "3.10", "3.11"]
        for django in ["3.2", "4.1", "4.2"]
        if (python, django)
        not in [
            ("3.7", "4.0"),
            ("3.7", "4.1"),
            ("3.7", "4.2"),
            ("3.11", "3.2"),
        ]
    ],
)
def tests_with_coverage(session: nox.Session, django: str) -> None:
    """
    Run the package's unit tests, with coverage report.

    """
    session.install(f"Django~={django}.0", ".[tests]")
    python_version = session.run(
        f"{session.bin}/python{session.python}", "--version", silent=True
    ).strip()
    django_version = session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "django",
        "--version",
        silent=True,
    ).strip()
    session.log(f"Running tests with {python_version}/Django {django_version}")
    session.run(f"{session.bin}/python{session.python}", "-Im", "coverage", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Wonce::DeprecationWarning",
        "-Im",
        "coverage",
        "run",
        "--source",
        PACKAGE_NAME,
        "runtests.py",
        env={"DJANGO_SETTINGS_MODULE": "tests.settings"},
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "coverage",
        "report",
        "--show-missing",
    )
    clean()


# Tasks which test the package's documentation.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["docs"])
def docs_build(session: nox.Session) -> None:
    """
    Build the package's documentation as HTML.

    """
    session.install(".[docs]")
    session.chdir("docs")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "sphinx",
        "-b",
        "html",
        "-d",
        f"{session.bin}/../tmp/doctrees",
        ".",
        f"{session.bin}/../tmp/html",
    )
    clean()


@nox.session(python=["3.11"], tags=["docs"])
def docs_docstrings(session: nox.Session) -> None:
    """
    Enforce the presence of docstrings on all modules, classes, functions, and
    methods.

    """
    session.install("interrogate")
    session.run(
        f"{session.bin}/python{session.python}", "-Im", "interrogate", "--version"
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "interrogate",
        "-v",
        "src/",
        "tests/",
        "noxfile.py",
    )
    clean()


@nox.session(python=["3.11"], tags=["docs"])
def docs_spellcheck(session: nox.Session) -> None:
    """
    Spell-check the package's documentation.

    """
    session.install("pyenchant", "sphinxcontrib-spelling", ".[docs]")
    build_dir = session.create_tmp()
    session.chdir("docs")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "sphinx",
        "-W",  # Promote warnings to errors, so that misspelled words fail the build.
        "-b",
        "spelling",
        "-d",
        f"{build_dir}/doctrees",
        ".",
        f"{build_dir}/html",
        # On Apple Silicon Macs, this environment variable needs to be set so
        # pyenchant can find the "enchant" C library. See
        # https://github.com/pyenchant/pyenchant/issues/265#issuecomment-1126415843
        env={"PYENCHANT_LIBRARY_PATH": os.getenv("PYENCHANT_LIBRARY_PATH", "")},
    )
    clean()


# Code formatting checks.
#
# These checks do *not* reformat code -- that happens in pre-commit hooks -- but will
# fail a CI build if they find any code that needs reformatting.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["formatters"])
def format_black(session: nox.Session) -> None:
    """
    Check code formatting with Black.

    """
    session.install("black")
    session.run(f"{session.bin}/python{session.python}", "-Im", "black", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "black",
        "--check",
        "--diff",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )
    clean()


@nox.session(python=["3.11"], tags=["formatters"])
def format_isort(session: nox.Session) -> None:
    """
    Check code formating with Black.

    """
    session.install("isort")
    session.run(f"{session.bin}/python{session.python}", "-Im", "isort", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "isort",
        "--check-only",
        "--diff",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )
    clean()


# Linters.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["linters", "security"])
def lint_bandit(session: nox.Session) -> None:
    """
    Lint code with the Bandit security analyzer.

    """
    session.install("bandit[toml]")
    session.run(f"{session.bin}/python{session.python}", "-Im", "bandit", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "bandit",
        "-c",
        "./pyproject.toml",
        "-r",
        "src/",
        "tests/",
    )
    clean()


@nox.session(python=["3.11"], tags=["linters"])
def lint_flake8(session: nox.Session) -> None:
    """
    Lint code with flake8.

    """
    session.install("flake8", "flake8-bugbear")
    session.run(f"{session.bin}/python{session.python}", "-Im", "flake8", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "flake8",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )
    clean()


@nox.session(python=["3.11"], tags=["linters"])
def lint_pylint(session: nox.Session) -> None:
    """
    Lint code with Pyling.

    """
    # Pylint requires that all dependencies be importable during the run, so unlike
    # other lint tasks we just install the package.
    session.install(".")
    session.install("pylint", "pylint-django")
    session.run(f"python{session.python}", "-Im", "pylint", "--version")
    session.run(f"python{session.python}", "-Im", "pylint", "src/", "tests/")


# Packaging checks.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["packaging"])
def package_build(session: nox.Session) -> None:
    """
    Check that the package builds.

    """
    clean()
    session.install("build")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build", "--version")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build")


@nox.session(python=["3.11"], tags=["packaging"])
def package_description(session: nox.Session) -> None:
    """
    Check that the package description will render on the Python Package Index.

    """
    package_dir = session.create_tmp()
    session.install("build", "twine")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build", "--version")
    session.run(f"{session.bin}/python{session.python}", "-Im", "twine", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "build",
        "--wheel",
        "--outdir",
        f"{package_dir}/build",
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "twine",
        "check",
        f"{package_dir}/build/*",
    )
    clean()


@nox.session(python=["3.11"], tags=["packaging"])
def package_manifest(session: nox.Session) -> None:
    """
    Check that the set of files in the package matches the set under version control.

    """
    session.install("check-manifest")
    session.run(
        f"{session.bin}/python{session.python}", "-Im", "check_manifest", "--version"
    )
    session.run(
        f"{session.bin}/python{session.python}", "-Im", "check_manifest", "--verbose"
    )
    clean()


@nox.session(python=["3.11"], tags=["packaging"])
def package_pyroma(session: nox.Session) -> None:
    """
    Check package quality with pyroma.

    """
    session.install("pyroma")
    session.run(
        f"{session.bin}/python{session.python}",
        "-c",
        'from importlib.metadata import version; print(version("pyroma"))',
    )
    session.run(f"{session.bin}/python{session.python}", "-Im", "pyroma", ".")
    clean()


@nox.session(python=["3.11"], tags=["packaging"])
def package_wheel(session: nox.Session) -> None:
    """
    Check the built wheel package for common errors.

    """
    package_dir = session.create_tmp()
    session.install("build", "check-wheel-contents")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "check_wheel_contents",
        "--version",
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "build",
        "--wheel",
        "--outdir",
        f"{package_dir}/build",
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "check_wheel_contents",
        f"{package_dir}/build",
    )
    clean()
