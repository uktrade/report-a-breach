class CompaniesHouseException(Exception):
    """Exception raised when issue encountered with Companies House API"""

    pass


class EmailNotVerifiedException(Exception):
    """Exception raised when user tries to save a breach object without verifying their email address."""

    pass


class CompaniesHouse500Error(Exception):
    """Exception raised when the Companies House API returns a 500 error"""

    pass
