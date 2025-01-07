from django.urls import reverse


class TestPrivateURLs:

    def test_private_urls_false(self, settings, use_include_private_urls, rasb_client):
        assert not settings.INCLUDE_PRIVATE_URLS
        # assert can access rasb urls
        response = rasb_client.post(
            reverse("report_a_suspected_breach:start"), data={"reporter_professional_relationship": "owner"}
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:email")
        # assert vasb urls return 404 not found
        response = rasb_client.get("/view/")
        assert response.status_code == 404

    # def test_private_urls_true(self, settings, rasb_client):
    #     settings.INCLUDE_PRIVATE_URLS = True
    #     assert settings.INCLUDE_PRIVATE_URLS
    #     # assert can access rasb urls
    #     response = rasb_client.post(
    #         reverse("report_a_suspected_breach:start"), data={"reporter_professional_relationship": "owner"}
    #     )
    #
    #     assert response.status_code == 302
    #     assert response.url == reverse("report_a_suspected_breach:email")
    #     # assert vasb urls return 403 forbidden
    #     response = rasb_client.get("/view/")
    #     assert response.status_code == 403
