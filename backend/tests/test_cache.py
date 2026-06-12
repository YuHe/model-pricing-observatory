from __future__ import annotations
import pytest
from app.cache import cache_key_hash, CACHE_TTLS


def test_cache_key_hash_deterministic():
    params = {"provider": "OpenAI", "page": 1}
    key1 = cache_key_hash("models:list", params)
    key2 = cache_key_hash("models:list", params)
    assert key1 == key2


def test_cache_key_hash_different_params():
    key1 = cache_key_hash("models:list", {"page": 1})
    key2 = cache_key_hash("models:list", {"page": 2})
    assert key1 != key2


def test_cache_ttls_defined():
    assert CACHE_TTLS["stats"] == 300
    assert CACHE_TTLS["models:detail"] == 600
    assert CACHE_TTLS["providers:list"] == 1800
