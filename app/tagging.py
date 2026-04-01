import re
from typing import Callable


def cmake_minimal_version_fail(log: str) -> bool:
    return "Compatibility with CMake < 3.5 has been removed" in log


def cmake_configure_error(log: str) -> bool:
    return (
        "CMake Error at" in log
        and re.search(r"-- Configuring incomplete, errors occurred!", log)
        is not None
    )


def cmake_boost(log: str) -> bool:
    return (
        "boost_systemConfig.cmake" in log
        and "(requested version 1.89.0)" in log
        and "lib/cmake/Boost-1.89.0" in log
    )


def python_build_deps_failure(log: str) -> bool:
    return bool(re.search(r"ERROR Missing dependencies:", log))


def python_import_error(log: str) -> bool:
    return bool(
        re.search(r"ImportError: cannot import name '.*' from '.*'", log)
    ) or bool(re.search(r"ModuleNotFoundError: No module named '.*'", log))


def python_runtime_deps_failure(log: str) -> bool:
    return (
        "pythonRuntimeDepsCheckHook" in log
        and "Checking runtime dependencies" in log
        and re.search(r"(not installed)|(not satisfied by version)", log)
        is not None
    )


def c_compile_error(log: str) -> bool:
    pattern = re.compile(r"^\S+\.[ch]{1,2}:\d+:\d+: error:", re.MULTILINE)
    return bool(pattern.search(log))


def npm_dependency_failure(log: str) -> bool:
    return "npm error" in log and (
        "can only install packages when your package.json and package-lock.json"
        in log
        or "failed to install dependencies" in log
    )


def pytest_failure(log: str) -> bool:
    summary = bool(re.search(r"==+ short test summary info ==+", log))
    return (
        summary and ("FAILED" in log or "!!!!!!!!!!!!!!!!!!!!" in log)
    ) or (
        summary
        and (
            bool(re.search(r"=============.*error(s?) in.*=============", log))
        )
    )


def hunk_failed(log: str) -> bool:
    return (
        "hunk FAILED -- saving rejects" in log
        or "hunks FAILED -- saving rejects" in log
        or "Skipping patch.\n1 out of 1 hunk ignored\n" in log
    )


def substitute_error(log: str) -> bool:
    return bool(re.search(r"substitute\(\): ERROR:", log)) or (
        "substituteStream() in derivation" in log
        and "ERROR: pattern" in log
        and "doesn't match anything in file" in log
    )


def python_missing_legacy_setup(log: str) -> bool:
    return (
        "compile(getattr(tokenize, 'open', open)(__file__).read()" in log
        and "FileNotFoundError: [Errno 2] No such file or directory: 'setup.py'"
        in log
    )


def python_backend_error(log: str) -> bool:
    return bool(
        re.search(r"BackendUnavailable|ERROR Backend .* is not available", log)
    )


def curl_fetch_error(log: str) -> bool:
    return (
        "curl: (22) The requested URL returned error: 404" in log
        and "error: cannot download source from any mirror" in log
    )


def hash_mismatch(log: str) -> bool:
    return "error: hash mismatch in fixed-output derivation" in log


def haskell_dep_failure(log: str) -> bool:
    return (
        "Error: [Cabal-8010]" in log
        and "Encountered missing or private dependencies:" in log
    )


def missing_header_file(log: str) -> bool:
    return (
        "#include <" in log
        and "compilation terminated." in log
        and ": No such file or directory" in log
    )


def autotools_configure(log: str) -> bool:
    return (
        "Running phase: updateAutotoolsGnuConfigScriptsPhase" in log
        and "Running phase: configurePhase"
        and "configure: erroor:" in log
    )


def sbcl_create_homeless_shelter(log: str) -> bool:
    return (
        "; compilation unit aborted" in log
        and "BUILD FAILED: Can't create directory /homeless-shelter" in log
    )


def sbcl_compilation_fail(log: str) -> bool:
    return (
        "SBCL is free software, provided as is, with absolutely no warranty" in log
        and "; compilation unit aborted" in log
    )


CHECKS: tuple[tuple[str, Callable[[str], bool]], ...] = (
    ("cmake/boost 1.89", cmake_boost),
    ("cmake/minimal-version-fail", cmake_minimal_version_fail),
    ("cmake/configure-error", cmake_configure_error),
    ("c-compile-error", c_compile_error),
    ("autotools-configure-error", autotools_configure),
    ("sbcl-create-homeless-shelter", sbcl_create_homeless_shelter),
    ("sbcl-compilation-fail", sbcl_compilation_fail),
    ("npm-dependency-failure", npm_dependency_failure),
    ("haskell-deps-failure", haskell_dep_failure),
    ("python/runtime-deps", python_runtime_deps_failure),
    ("python/missing-legacy-setup", python_missing_legacy_setup),
    ("python/import-error", python_import_error),
    ("python/backend-error", python_backend_error),
    ("python/build-deps-failure", python_build_deps_failure),
    ("python/pytest-failure", pytest_failure),
    ("generic/missing-header", missing_header_file),
    ("generic/fetch-error", curl_fetch_error),
    ("generic/hash-mismatch", hash_mismatch),
    ("generic/hunk-failed", hunk_failed),
    ("generic/substitute-error", substitute_error),
)
