# dataset_cat/scripts/lint_runner.py
import subprocess
import sys
from typing import List


def run_command(command: List[str]) -> int:
    """
    Runs a given command as a subprocess.

    Prints the command being run, and its stdout/stderr.

    Args:
        command: A list of strings representing the command and its arguments.

    Returns:
        The exit code of the command.
    """
    print(f"Running: {' '.join(command)}")
    # When this script is run via `poetry run lint`, the environment
    # should already be configured to find black, isort, etc.
    process = subprocess.run(
        command, capture_output=True, text=True, check=False, shell=False
    )  # Added shell=False for clarity
    if process.stdout:
        print("--- stdout ---")
        print(process.stdout.strip())
        print("--- end stdout ---")
    if process.stderr:
        print("--- stderr ---", file=sys.stderr)
        print(process.stderr.strip(), file=sys.stderr)
        print("--- end stderr ---", file=sys.stderr)
    return process.returncode


def main() -> None:
    """
    Main entry point for the linting script.

    Executes a series of linting tools (ruff, mypy, black --check, isort --check-only)
    and reports on their success or failure. Exits with 0 if all checks pass,
    1 otherwise.
    """
    print("Starting linting process...")
    # Ensure tools are run from the project root, which should be the CWD
    # if `poetry run lint` is executed from the project root.
    # Use sys.executable to ensure tools are run with the correct Python interpreter
    python_executable = sys.executable
    lint_commands: List[List[str]] = [
        [python_executable, "-m", "ruff", "check", "."],
        [python_executable, "-m", "mypy", "."],
        [python_executable, "-m", "black", "--check", "."],
        [python_executable, "-m", "isort", "--check-only", "--diff", "."],
    ]

    all_passed = True
    for cmd_args in lint_commands:
        print(f"\n{'=' * 10} Executing: {' '.join(cmd_args)} {'=' * 10}")
        return_code = run_command(cmd_args)
        if return_code != 0:
            # Corrected f-string:
            print(f"Command {' '.join(cmd_args)} FAILED with exit code {return_code}")
            all_passed = False
        else:
            # Corrected f-string:
            print(f"Command {' '.join(cmd_args)} PASSED.")

    print(f"\n{'=' * 30}")
    if all_passed:
        print("All lint checks passed successfully!")
        sys.exit(0)
    else:
        print("Some lint checks FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
