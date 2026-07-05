"""Fixtures for the retrieval-system tests.

Everything runs against a COPY of the mini entity tree in tmp_path — the real
tree is never touched, and every component takes explicit paths by design
(no monkeypatching engine.cli._paths).
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "entity_tree"


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    """A fake repo root whose vape/entity is the fixture tree."""
    dest = tmp_path / "repo"
    shutil.copytree(FIXTURES, dest / "vape" / "entity")
    return dest


@pytest.fixture()
def core(root: Path):
    from engine.memory.core_store import CoreStore
    store = CoreStore(root / "vape" / "entity" / "storage" / "index" / "core.db")
    yield store
    store.close()


@pytest.fixture()
def sqlite_backend(root: Path):
    from vibe_plugin_retrieval_sqlite import SqliteBackend
    b = SqliteBackend(root, {}, None)
    b.migrate()
    return b


@pytest.fixture()
def indexer(root: Path, core, sqlite_backend):
    from engine.memory.indexer import Indexer
    return Indexer(root, core, sqlite_backend)


@pytest.fixture()
def firewall(root: Path, core, sqlite_backend):
    from engine.memory.files_backend import FilesBackend
    from engine.memory.firewall import Firewall
    return Firewall(sqlite_backend, root, floor=FilesBackend(root), core_store=core)
