import pytest
from app.services.google_search import GoogleSearchService
from app.models.google_search import GoogleSearchResult
from app.core.config import settings

class TestGoogleSearchService:
    @pytest.fixture
    def service(self):
        return GoogleSearchService()

    def test_zhihu_search_real_api(self, service):
        if not settings.GOOGLE_API_KEY or not settings.GOOGLE_CX_ID:
            pytest.skip("Missing Google API credentials")
        result = service.search(
            query="网球拍推荐",
            site_filter="zhihu.com",
            date_restrict="y2",
            num_results=3
        )

        print("result: ",result)

        assert isinstance(result, GoogleSearchResult)
        assert len(result.items) > 0

        for item in result.items:
            assert "zhihu.com" in item.link
            
        for item in result.items:
            assert item.title.strip() != ""
            assert item.snippet.strip() != ""
