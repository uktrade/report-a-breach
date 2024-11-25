# import re
#
# from playwright.sync_api import expect
#
# from .. import conftest
#
#
# class TestUploadDocuments(conftest.PlaywrightTestBase):
#     """
#     Tests for the upload documents page
#     """
#
#     def test_no_input_goes_to_suspected_breach(self):
#         self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
#         self.page.get_by_role("link", name="Your details").click()
#         self.create_reporter_details(self.page, "I'm an owner")
#         self.page.get_by_role("link", name="2. About the person or").click()
#         self.create_non_uk_breacher(self.page)
#         self.page.get_by_role("link", name="Overview of the suspected breach").click()
#         self.overview_of_breach(self.page)
#         self.page.get_by_role("link", name="The supply chain").click()
#         self.create_uk_supplier(self.page)
#         self.no_end_users(self.page)
#         self.page.get_by_role("heading", name="Were there any other").click()
#         self.page.get_by_label("Yes").check()
#         self.page.get_by_text("Give all addresses").click()
#         self.page.get_by_label("Give all addresses").fill("Addr supply chain")
#         self.page.get_by_role("button", name="Continue").click()
#         self.page.get_by_role("heading", name="Upload documents (optional)").click()
#         self.page.get_by_text("You can upload items such as").click()
#         self.page.get_by_text("Drag and drop files here or").click()
#         self.page.get_by_text("Choose files").click()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/tell_us_about_the_suspected_breach"))
#
#     def test_correct_files_goes_to_suspected_breach(self):
#         self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
#         self.page.get_by_role("link", name="Your details").click()
#         self.create_reporter_details(self.page, "I'm an owner")
#         self.page.get_by_role("link", name="2. About the person or").click()
#         self.create_non_uk_breacher(self.page)
#         self.page.get_by_role("link", name="Overview of the suspected breach").click()
#         self.overview_of_breach(self.page)
#         self.page.get_by_role("link", name="The supply chain").click()
#         self.create_uk_supplier(self.page)
#         self.no_end_users(self.page)
#         self.page.get_by_role("heading", name="Were there any other").click()
#         self.page.get_by_label("Yes").check()
#         self.page.get_by_text("Give all addresses").click()
#         self.page.get_by_label("Give all addresses").fill("Addr supply chain")
#         self.page.get_by_role("button", name="Continue").click()
#         self.upload_documents_page(self.page, files=["./tests/test_frontend/testfiles/testfile.pdf"])
#
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/tell_us_about_the_suspected_breach"))
#
#     def test_incorrect_filetype_raises_error(self):
#         self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
#         self.page.get_by_role("link", name="Your details").click()
#         self.create_reporter_details(self.page, "I'm an owner")
#         self.page.get_by_role("link", name="2. About the person or").click()
#         self.create_non_uk_breacher(self.page)
#         self.page.get_by_role("link", name="Overview of the suspected breach").click()
#         self.overview_of_breach(self.page)
#         self.page.get_by_role("link", name="The supply chain").click()
#         self.create_uk_supplier(self.page)
#         self.no_end_users(self.page)
#         self.page.get_by_role("heading", name="Were there any other").click()
#         self.page.get_by_label("Yes").check()
#         self.page.get_by_text("Give all addresses").click()
#         self.page.get_by_label("Give all addresses").fill("Addr supply chain")
#         self.page.get_by_role("button", name="Continue").click()
#         self.upload_documents_page(self.page, files=["./tests/test_frontend/testfiles/missing_filetype"])
#         expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
#         expect(self.page.get_by_role("button", name="Continue")).to_be_visible()
#         expect(self.page).to_have_url(re.compile(r".*/tell_us_about_the_suspected_breach"))
#
#     def test_malware_file_raises_error(self):
#         self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
#         self.page.get_by_role("link", name="Your details").click()
#         self.create_reporter_details(self.page, "I'm an owner")
#         self.page.get_by_role("link", name="2. About the person or").click()
#         self.create_non_uk_breacher(self.page)
#         self.page.get_by_role("link", name="Overview of the suspected breach").click()
#         self.overview_of_breach(self.page)
#         self.page.get_by_role("link", name="The supply chain").click()
#         self.create_uk_supplier(self.page)
#         self.no_end_users(self.page)
#         self.page.get_by_role("heading", name="Were there any other").click()
#         self.page.get_by_label("Yes").check()
#         self.page.get_by_text("Give all addresses").click()
#         self.page.get_by_label("Give all addresses").fill("Addr supply chain")
#         self.page.get_by_role("button", name="Continue").click()
#         self.upload_documents_page(self.page, files=["./tests/test_frontend/testfiles/malware_file_eicar.txt"])
#         expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
#         expect(self.page.get_by_role("link", name="A virus was found in one of the files you uploaded.")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/tell_us_about_the_suspected_breach"))
