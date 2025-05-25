import pytest
from dataset_cat.crawler import Crawler

@pytest.mark.integration
@pytest.mark.parametrize("source_name", Crawler.get_sources())
def test_source_integration(source_name):
    """
    Integration test for each source to ensure it can fetch data correctly.
    """
    tags = "Rem"  # Example tag for testing
    limit = 2
    size = "large"
    strict = False

    result, message = Crawler.start_crawl(source_name, tags, limit, size, strict)

    assert result is not None, f"{source_name} returned None: {message}"
    assert len(result) > 0, f"{source_name} returned no results: {message}"
    assert len(result) <= limit, f"{source_name} returned more than the limit: {len(result)}"
    print(f"{source_name} passed with {len(result)} results.")
