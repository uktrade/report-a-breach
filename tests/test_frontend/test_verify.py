# EMAIL_DETAILS = {'email': 'test@digital.gov.uk', 'verify_code': '012345'}

# @classmethod
#     def verify_email_step(cls, details=EMAIL_DETAILS):
#         #
#         # Email page
#         #
#         cls.page.get_by_label("What is your email address?").click()
#         cls.page.get_by_label("What is your email address?").fill(details['email'])
#         cls.page.get_by_role("button", name="Continue").click()
#         #
#         # Verify Page
#         #
#         cls.page.get_by_label("We've sent you an email").click()
#         cls.page.get_by_label("We've sent you an email").fill(details['verify_code'])
#         cls.page.get_by_role("button", name="Continue").click()
