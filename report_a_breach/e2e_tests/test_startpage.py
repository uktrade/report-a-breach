# from playwright.sync_api import Page, expect

# class Test_Verify:
#     def test_user_verify(self, page: Page):
#         page.goto("http://localhost:8000/report_a_breach/email/")
#         page.get_by_label("What is your email address?").click()
#         page.get_by_label("What is your email address?").fill("tests@digital.gov.uk")
#         page.get_by_role("button", name="Continue").click()
#         page.get_by_label("We've sent you an email").click()
#         page.get_by_label("We've sent you an email").fill("012345")
#         page.get_by_role("button", name="Continue").click()
#         page.get_by_text("Are you reporting a business").click()
