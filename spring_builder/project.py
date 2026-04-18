import os
import shutil
import stat
import subprocess
import sys
import zipfile
from io import BytesIO


def _remove_readonly(func, path, _exc_info):
    """Clear read-only flag and retry removal (needed for .git on Windows)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _clear_directory(target_dir):
    """Remove all contents of a directory except .git."""
    for entry in os.listdir(target_dir):
        if entry == ".git":
            continue
        path = os.path.join(target_dir, entry)
        if os.path.isdir(path):
            shutil.rmtree(path, onexc=_remove_readonly)
        else:
            os.remove(path)


def extract_project(zip_bytes, target_dir):
    """Extract the zip into the target directory, preserving .git if present."""
    if os.path.exists(target_dir):
        overwrite = input(f"\nDirectory '{target_dir}' already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != "y":
            print("Aborted.")
            sys.exit(1)
        _clear_directory(target_dir)

    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        zf.extractall(target_dir)
    print(f"Project extracted to: {os.path.abspath(target_dir)}")


def build_and_test(project_dir, project_type):
    """Build the project and run tests."""
    abs_dir = os.path.abspath(project_dir)
    print(f"\n{'='*60}")
    print("Building project and running tests...")
    print(f"{'='*60}\n")

    if project_type == "maven-project":
        wrapper_unix = "mvnw"
        wrapper_win = "mvnw.cmd"
    else:
        wrapper_unix = "gradlew"
        wrapper_win = "gradlew.bat"

    if sys.platform == "win32":
        wrapper_path = os.path.join(abs_dir, wrapper_win)
        cmd = [wrapper_path, "clean", "test"]
    else:
        wrapper_path = os.path.join(abs_dir, wrapper_unix)
        os.chmod(wrapper_path, 0o755)
        cmd = [wrapper_path, "clean", "test"]

    result = subprocess.run(
        cmd,
        cwd=abs_dir,
        timeout=300,
    )

    if result.returncode == 0:
        print(f"\n{'='*60}")
        print("BUILD SUCCESS - All tests passed!")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"BUILD FAILED (exit code {result.returncode})")
        print(f"{'='*60}")
        sys.exit(result.returncode)


def generate_github_actions(project_dir, project_type, java_version):
    """Generate a GitHub Actions workflow that runs tests on push and manual trigger."""
    abs_dir = os.path.abspath(project_dir)
    workflows_dir = os.path.join(abs_dir, ".github", "workflows")
    os.makedirs(workflows_dir, exist_ok=True)

    if project_type == "maven-project":
        build_cmd = "./mvnw clean test"
        cache = "maven"
        report_paths = "**/surefire-reports/TEST-*.xml"
    else:
        build_cmd = "./gradlew clean test"
        cache = "gradle"
        report_paths = "**/build/test-results/test/TEST-*.xml"

    workflow = f"""name: Java CI

on:
  push:
    branches: [ "**" ]
  pull_request:
    branches: [ "**" ]
  workflow_dispatch:

permissions:
  contents: read
  checks: write

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK {java_version}
        uses: actions/setup-java@v4
        with:
          java-version: '{java_version}'
          distribution: 'temurin'
          cache: '{cache}'

      - name: Run tests
        run: |
          chmod +x {build_cmd.split()[0]}
          {build_cmd}

      - name: Test Report
        uses: dorny/test-reporter@v1
        if: success() || failure()
        with:
          name: Test Results
          path: '{report_paths}'
          reporter: java-junit
"""

    workflow_path = os.path.join(workflows_dir, "ci.yml")
    with open(workflow_path, "w", newline="\n") as f:
        f.write(workflow)

    print(f"\nGitHub Actions workflow generated: .github/workflows/ci.yml")
