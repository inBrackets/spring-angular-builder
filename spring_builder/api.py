import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

INITIALIZR_URL = "https://start.spring.io"

# The Initializr API returns version IDs with legacy suffixes (.RELEASE,
# .BUILD-SNAPSHOT) but Maven Central uses bare versions (e.g. 4.0.5 not
# 4.0.5.RELEASE). Strip these suffixes so the generated pom/build file
# resolves correctly.
VERSION_SUFFIX_MAP = {
    ".RELEASE": "",
    ".BUILD-SNAPSHOT": "-SNAPSHOT",
}


def normalize_boot_version(version_id):
    """Convert Initializr version ID to Maven-compatible version string."""
    for suffix, replacement in VERSION_SUFFIX_MAP.items():
        if version_id.endswith(suffix):
            return version_id[: -len(suffix)] + replacement
    return version_id


def fetch_metadata():
    """Fetch available options from Spring Initializr API."""
    req = Request(INITIALIZR_URL, headers={"Accept": "application/json"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def download_project(params):
    """Download the generated project zip from Spring Initializr."""
    query = urlencode(params, doseq=True)
    url = f"{INITIALIZR_URL}/starter.zip?{query}"
    print(f"\nDownloading project from Spring Initializr...")
    req = Request(url)
    with urlopen(req, timeout=60) as resp:
        return resp.read()
