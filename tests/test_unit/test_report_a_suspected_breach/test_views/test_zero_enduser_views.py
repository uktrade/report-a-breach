# TODO: To be updated in DST-511

# from django.http import HttpResponseRedirect
# from django.urls import reverse_lazy
#
#
# class TestZeroEndUsersView:
#     def test_add_an_end_user_post(self, rasb_client):
#         response = rasb_client.post(
#             reverse_lazy("report_a_suspected_breach:zero_end_users"),
#             data={
#                 "do_you_want_to_add_an_end_user": True,
#             },
#         )
#
#         expected_redirect = HttpResponseRedirect(
#             status=302,
#             content_type="text/html; charset=utf-8",
#             redirect_to="/report_a_suspected_breach/where_were_the_goods_supplied_to/?add_another_end_user=yes",
#         )
#
#         assert response.status_code == expected_redirect.status_code
#         assert response["content-type"] == expected_redirect["content-type"]
#         assert response.url == expected_redirect.url
#
#     def test_do_not_add_an_end_user_post(self, rasb_client):
#         response = rasb_client.post(
#             reverse_lazy("report_a_suspected_breach:zero_end_users"),
#             data={
#                 "do_you_want_to_add_an_end_user": False,
#             },
#         )
#         expected_redirect = HttpResponseRedirect(
#             status=302,
#             content_type="text/html; charset=utf-8",
#             redirect_to="/report_a_suspected_breach/were_there_other_addresses_in_the_supply_chain/",
#         )
#
#         assert response.status_code == expected_redirect.status_code
#         assert response["content-type"] == expected_redirect["content-type"]
#         assert response.url == expected_redirect.url
#
#     def test_add_an_end_user_made_available_post(self, rasb_client):
#         session = rasb_client.session
#         session["made_available_journey"] = True
#         session.save()
#         response = rasb_client.post(
#             reverse_lazy("report_a_suspected_breach:zero_end_users"),
#             data={
#                 "do_you_want_to_add_an_end_user": True,
#             },
#         )
#
#         expected_redirect = HttpResponseRedirect(
#             status=302,
#             content_type="text/html; charset=utf-8",
#             redirect_to="/report_a_suspected_breach/where_were_the_goods_made_available_to/?add_another_end_user=yes",
#         )
#
#         assert response.status_code == expected_redirect.status_code
#         assert response["content-type"] == expected_redirect["content-type"]
#         assert response.url == expected_redirect.url
#
#     def test_do_not_add_an_end_user_made_available_post(self, rasb_client):
#         session = rasb_client.session
#         session["made_available_journey"] = True
#         session.save()
#         response = rasb_client.post(
#             reverse_lazy("report_a_suspected_breach:zero_end_users"),
#             data={
#                 "do_you_want_to_add_an_end_user": False,
#             },
#         )
#
#         expected_redirect = HttpResponseRedirect(
#             status=302,
#             content_type="text/html; charset=utf-8",
#             redirect_to="/report_a_suspected_breach/were_there_other_addresses_in_the_supply_chain/",
#         )
#
#         assert response.status_code == expected_redirect.status_code
#         assert response["content-type"] == expected_redirect["content-type"]
#         assert response.url == expected_redirect.url
