# dataset_cat/scripts/format_runner.py
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
    process = subprocess.run(
        command, capture_output=True, text=True, check=False, shell=False
    )  # Added shell=False for clarity, though it's default
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
    Main entry point for the formatting script.

    Executes a series of formatting tools (black, isort) to reformat
    the codebase. Reports on their success or failure. Exits with 0
    if all tools run successfully, 1 otherwise.
    """
    print("Starting formatting process...")
    # Use sys.executable to ensure tools are run with the correct Python interpreter
    python_executable = sys.executable
    format_commands: List[List[str]] = [
        [python_executable, "-m", "black", "."],
        [python_executable, "-m", "isort", "."],
    ]

    all_succeeded = True
    for cmd_args in format_commands:
        print(f"\n{'=' * 10} Executing: {' '.join(cmd_args)} {'=' * 10}")
        return_code = run_command(cmd_args)
        if return_code != 0:
            print(f"Command {' '.join(cmd_args)} FAILED with exit code {return_code}")
            all_succeeded = False
        else:
            print(f"Command {' '.join(cmd_args)} COMPLETED.")

    print(f"\n{'=' * 30}")
    if all_succeeded:
        print("All formatting tasks completed successfully!")
        sys.exit(0)
    else:
        print("Some formatting tasks FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
