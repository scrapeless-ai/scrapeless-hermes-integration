# Documentation checklist

## Source

https://hermes-agent.nousresearch.com/docs/getting-started/installation

## Checklist

Prerequisites and setup decisions stated on the page:

1. Provide the base host utilities for the POSIX script — "provide Git, curl, tar, and SHA-256 utilities."
2. Use the current Python runtime — "Current first-party installations run on **Python 3.14**," with the `>=3.11,<3.15` range only allowing older installs to run the updater before PM switches them.
3. Let the installer supply its own uv — "The script always downloads its verified uv pin; a uv already on your PATH is never used."

Selected first three items from the actual October 29, 2026 output. The full local run contains 15 numbered checklist items and platform notes.
