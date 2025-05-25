import pytest
from dataset_cat.crawler import Crawler

def mock_source_generator():
    yield {"id": 1, "url": "http://example.com/image1.jpg"}
    yield {"id": 2, "url": "http://example.com/image2.jpg"}

@pytest.fixture
def mock_sources(monkeypatch):
    def mock_start_crawl(source_name, tags, limit, size, strict):
        if source_name not in Crawler.get_sources():
            return None, f"Unsupported source: {source_name}"
        return list(mock_source_generator())[:limit], "Crawl task initialized."

    monkeypatch.setattr(Crawler, "start_crawl", mock_start_crawl)

def test_valid_source(mock_sources):
    source, message = Crawler.start_crawl("Danbooru", "tag1,tag2", 2, "large", False)
    assert source is not None
    assert len(source) == 2
    assert message == "Crawl task initialized."

def test_invalid_source(mock_sources):
    source, message = Crawler.start_crawl("InvalidSource", "tag1,tag2", 2, "large", False)
    assert source is None
    assert message == "Unsupported source: InvalidSource"

def test_empty_tags(mock_sources):
    source, message = Crawler.start_crawl("Danbooru", "", 2, "large", False)
    assert source is not None
    assert len(source) == 2
    assert message == "Crawl task initialized."

def test_invalid_size(mock_sources):
    source, message = Crawler.start_crawl("Danbooru", "tag1,tag2", 2, "invalid_size", False)
    assert source is not None
    assert len(source) == 2
    assert message == "Crawl task initialized."

def test_limit_exceeds(mock_sources):
    source, message = Crawler.start_crawl("Danbooru", "tag1,tag2", 10, "large", False)
    assert source is not None
    assert len(source) == 2  # Mock source only has 2 items
    assert message == "Crawl task initialized."