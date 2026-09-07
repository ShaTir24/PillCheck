.PHONY: download-data build-splits eval-baseline

download-data:
	uv run python scripts/download_epillid.py
	uv run python scripts/download_ndc.py
	@echo "--- c3pi and pillbox need a manually-resolved URL first (see their manifests) ---"
	-uv run python scripts/download_c3pi.py
	-uv run python scripts/download_pillbox.py

build-splits:
	uv run python scripts/join_metadata.py
	uv run python scripts/test_join.py
	uv run python scripts/build_splits.py

eval-baseline:
	uv run python eval/harness.py
