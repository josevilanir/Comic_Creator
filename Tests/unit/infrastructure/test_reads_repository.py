import os
import json
import pytest
from pathlib import Path
from src.infrastructure.persistence.reads_repository import ReadsRepository

@pytest.fixture
def temp_json(tmp_path):
    p = tmp_path / "reads_test.json"
    return str(p)

def test_reads_repository_initialization(temp_json):
    repo = ReadsRepository(temp_json)
    assert os.path.exists(temp_json)
    assert Path(temp_json).read_text() == "{}"

def test_reads_repository_toggle(temp_json):
    repo = ReadsRepository(temp_json)
    manga = "Test Manga"
    filename = "chapter1.pdf"
    
    # Toggle on
    is_read = repo.toggle(manga, filename)
    assert is_read is True
    assert repo.is_read(manga, filename) is True
    assert filename in repo.get_reads(manga)
    
    # Toggle off
    is_read = repo.toggle(manga, filename)
    assert is_read is False
    assert repo.is_read(manga, filename) is False
    assert filename not in repo.get_reads(manga)

def test_reads_repository_multiple_mangas(temp_json):
    repo = ReadsRepository(temp_json)
    repo.toggle("Manga A", "c1.pdf")
    repo.toggle("Manga B", "c2.pdf")
    
    assert "c1.pdf" in repo.get_reads("Manga A")
    assert "c2.pdf" in repo.get_reads("Manga B")
    assert "c1.pdf" not in repo.get_reads("Manga B")
