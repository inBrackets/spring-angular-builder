import os
import shutil
import subprocess
import sys
import zipfile
from io import BytesIO


def extract_project(zip_bytes, target_dir):
    """Extract the zip into the target directory."""
    if os.path.exists(target_dir):
        overwrite = input(f"\nDirectory '{target_dir}' already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != "y":
            print("Aborted.")
            sys.exit(1)
        shutil.rmtree(target_dir)

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
