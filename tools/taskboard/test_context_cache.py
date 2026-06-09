#!/usr/bin/env python3
"""Tests for the project context caching system in project_context.py and ai_router.py.

Verifies:
  1. Cache file is created on first call
  2. Cache is reused on subsequent calls (no re-generation)
  3. Expired cache is regenerated
  4. refresh_context_cache() works
"""

import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import project_context
import ai_router

# ── Helpers ────────────────────────────────────────────────────────────────

def _test_cache_creation():
    """Test that get_cached_project_context creates a cache file on first call."""
    # Point cache to a temp dir
    tmpdir = tempfile.mkdtemp(prefix="tb_ctx_test_")
    try:
        orig_dir = project_context.CONTEXT_CACHE_DIR
        orig_ttl = project_context.CONTEXT_CACHE_TTL_SECONDS
        project_context.CONTEXT_CACHE_DIR = tmpdir
        project_context.CONTEXT_CACHE_TTL_SECONDS = 3600

        # Clear any existing cache for this test
        cache_path = project_context._cache_path("taskboard")
        if os.path.exists(cache_path):
            os.unlink(cache_path)

        # First call: should generate and cache
        ctx1 = ai_router.get_cached_project_context("taskboard")
        assert ctx1, "Context should not be empty"
        assert "TASKBOARD" in ctx1, "Context should contain taskboard header"
        assert os.path.exists(cache_path), f"Cache file should exist at {cache_path}"

        # Second call: should use cache (no subprocess)
        mtime1 = os.path.getmtime(cache_path)
        ctx2 = ai_router.get_cached_project_context("taskboard")
        mtime2 = os.path.getmtime(cache_path)
        assert ctx2 == ctx1, "Cached context should be identical"
        assert mtime2 == mtime1, "Cache file should NOT have been regenerated"

        project_context.CONTEXT_CACHE_DIR = orig_dir
        project_context.CONTEXT_CACHE_TTL_SECONDS = orig_ttl
        print("  * test_cache_creation passed")
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def _test_cache_expiry():
    """Test that expired cache is regenerated."""
    tmpdir = tempfile.mkdtemp(prefix="tb_ctx_test_")
    try:
        orig_dir = project_context.CONTEXT_CACHE_DIR
        orig_ttl = project_context.CONTEXT_CACHE_TTL_SECONDS
        project_context.CONTEXT_CACHE_DIR = tmpdir
        project_context.CONTEXT_CACHE_TTL_SECONDS = 3600

        cache_path = project_context._cache_path("taskboard")
        if os.path.exists(cache_path):
            os.unlink(cache_path)

        # Generate fresh cache
        ctx1 = ai_router.get_cached_project_context("taskboard")
        assert os.path.exists(cache_path)

        # Manually age the cache file (set mtime to 2 hours ago)
        old_time = time.time() - 7200  # 2h ago, older than 1h TTL
        os.utime(cache_path, (old_time, old_time))

        # This should trigger regeneration
        ctx2 = ai_router.get_cached_project_context("taskboard")
        assert ctx2, "Context should not be empty after regeneration"
        mtime_new = os.path.getmtime(cache_path)
        assert mtime_new > old_time, "Cache file mtime should be updated (regenerated)"

        project_context.CONTEXT_CACHE_DIR = orig_dir
        project_context.CONTEXT_CACHE_TTL_SECONDS = orig_ttl
        print("  * test_cache_expiry passed")
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def _test_refresh_context_cache():
    """Test that refresh_context_cache() works for both scopes."""
    tmpdir = tempfile.mkdtemp(prefix="tb_ctx_test_")
    try:
        orig_dir = project_context.CONTEXT_CACHE_DIR
        project_context.CONTEXT_CACHE_DIR = tmpdir

        # Refresh both scopes
        result = ai_router.refresh_context_cache()
        assert result["ok"], f"Refresh should succeed: {result}"
        assert len(result["scopes"]) == 2, "Should refresh both scopes"

        for s in result["scopes"]:
            assert s["ok"], f"Scope {s['scope']} should be ok"
            assert s["size"] > 0, f"Scope {s['scope']} should have content"
            cache_path = project_context._cache_path(s["scope"])
            assert os.path.exists(cache_path), f"Cache file should exist for {s['scope']}"

        # Refresh single scope
        result2 = ai_router.refresh_context_cache("taskboard")
        assert result2["ok"], "Single-scope refresh should succeed"
        assert len(result2["scopes"]) == 1
        assert result2["scopes"][0]["scope"] == "taskboard"

        project_context.CONTEXT_CACHE_DIR = orig_dir
        print("  * test_refresh_context_cache passed")
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def _test_empty_cache_fallback():
    """Test that load_cached returns None for missing/empty cache."""
    tmpdir = tempfile.mkdtemp(prefix="tb_ctx_test_")
    try:
        orig_dir = project_context.CONTEXT_CACHE_DIR
        project_context.CONTEXT_CACHE_DIR = tmpdir

        # No cache file → None
        result = project_context.load_cached("nonexistent")
        assert result is None, "Non-existent cache should return None"

        # Empty cache file → None
        cache_path = project_context._cache_path("taskboard")
        with open(cache_path, "w") as f:
            f.write("   \n")  # whitespace only
        result2 = project_context.load_cached("taskboard")
        assert result2 is None, "Whitespace-only cache should return None"

        # Valid but expired → None
        with open(cache_path, "w") as f:
            f.write("valid content")
        old_time = time.time() - 999999  # way in the past
        os.utime(cache_path, (old_time, old_time))
        result3 = project_context.load_cached("taskboard")
        assert result3 is None, "Expired cache should return None"

        project_context.CONTEXT_CACHE_DIR = orig_dir
        print("  * test_empty_cache_fallback passed")
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    all_ok = True
    tests = [
        ("test_cache_creation", _test_cache_creation),
        ("test_cache_expiry", _test_cache_expiry),
        ("test_refresh_context_cache", _test_refresh_context_cache),
        ("test_empty_cache_fallback", _test_empty_cache_fallback),
    ]
    for name, fn in tests:
        try:
            print(f"Running {name}...")
            fn()
        except Exception as e:
            print(f"  - {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            all_ok = False

    if all_ok:
        print("\nAll context cache tests passed!")
    else:
        print("\nSome tests failed!")
        sys.exit(1)
