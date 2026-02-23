#!/bin/bash
# Shela Test Runner
# Re-organize/Refactor support: ensures core/ and forge/ are in PYTHONPATH

export PYTHONPATH=$PYTHONPATH:$(pwd)/core:$(pwd)/forge
.venv/bin/pytest tests/
