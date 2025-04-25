import os
import subprocess

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.network import setup_allowed_hosts
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict


class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        validate_default=False,
    )

    debug: bool = False
    django_secret_key: str
    rab_allowed_hosts: list[str] = ["*"]

    clam_av_username: str = ""
    clam_av_password: str = ""
    clam_av_domain: str = ""

    companies_house_api_key: str | None = None

    gov_notify_api_key: str = ""
    email_verify_code_template_id: str = ""
    restrict_sending: bool = True
    email_vasb_user_admin_template_id: str = ""
    email_user_report_confirmation_template_id: str = ""
    otsi_new_application_template_id: str = ""
    new_breach_reported_alert_recipients: str = "email@example.com"

    sentry_dsn: str = ""
    sentry_environment: str = ""
    sentry_enable_tracing: bool = False
    sentry_traces_sample_rate: float = 0.0

    gtm_enabled: bool = True
    gtm_id: str = ""

    temporary_s3_bucket_access_key_id: str = "test"
    temporary_s3_bucket_secret_access_key: str = "test"

    permanent_s3_bucket_access_key_id: str = "test"
    permanent_s3_bucket_secret_access_key: str = "test"

    aws_default_region: str = "eu-west-2"
    temporary_s3_bucket_name: str = "temporary-document-bucket"
    permanent_s3_bucket_name: str = "permanent-document-bucket"
    presigned_url_expiry_seconds: int = 3600

    include_private_urls: bool = False

    # Django sites
    report_a_suspected_breach_domain: str = "report-a-suspected-breach"
    view_a_suspected_breach_domain: str = "view-a-suspected-breach"
    report_a_suspected_breach_extra_domain: str = ""
    view_a_suspected_breach_extra_domain: str = ""
    report_a_suspected_breach_service_domain: str = ""
    view_a_suspected_breach_service_domain: str = ""

    # SSO
    authbroker_url: str = ""
    authbroker_client_id: str = ""
    authbroker_client_secret: str = ""
    authbroker_token_session_key: str = ""
    authbroker_staff_sso_scope: str = "read"

    # Mock SSO
    # todo - can we delete this
    mock_sso_token: str = ""
    mock_sso_scope: str = "read"
    mock_sso_username: str = ""
    mock_sso_email_user_id: str = ""
    oauthlib_insecure_transport: int = 0

    # Redis
    redis_host: str = ""
    redis_port: int = 6379

    # CSP settings
    csp_report_only: bool = True
    csp_report_uri: str | None = None

    # Information about the current environment
    current_branch: str = Field(alias="GIT_BRANCH", default="unknown")
    current_tag: str = Field(alias="GIT_TAG", default="")
    current_commit: str = Field(alias="GIT_COMMIT", default="")

    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        return self.rab_allowed_hosts

    @computed_field
    @property
    def temporary_s3_bucket_configuration(self) -> dict[str, str]:
        return {
            "bucket_name": self.temporary_s3_bucket_name,
            "access_key_id": self.temporary_s3_bucket_access_key_id,
            "secret_access_key": self.temporary_s3_bucket_secret_access_key,
        }

    @computed_field
    @property
    def permanent_s3_bucket_configuration(self) -> dict[str, str]:
        return {
            "bucket_name": self.permanent_s3_bucket_name,
            "access_key_id": self.permanent_s3_bucket_access_key_id,
            "secret_access_key": self.permanent_s3_bucket_secret_access_key,
        }


class LocalSettings(BaseSettings):
    database_uri: str = Field(alias="DATABASE_URL")
    profiling_enabled: bool = False
    localstack_port: int = 14566

    @computed_field
    @property
    def git_current_branch(self) -> str:
        current_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True)
        if current_branch.returncode == 0:
            return current_branch.stdout.decode("utf-8").replace("\n", "")
        else:
            return "unknown"

    @computed_field
    @property
    def git_current_commit(self) -> str:
        current_commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True)
        if current_commit.returncode == 0:
            return current_commit.stdout.decode("utf-8").replace("\n", "")
        else:
            return "unknown"


class TestSettings(LocalSettings):
    headless: bool = False
    save_videos: bool = False  # Save videos of the tests


class DBTPlatformSettings(BaseSettings):
    in_build_step: bool = Field(alias="BUILD_STEP", default=False)

    # Redis env vars
    redis_endpoint: str = Field(alias="REDIS_ENDPOINT", default="")

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        if self.in_build_step:
            return self.rab_allowed_hosts
        else:
            return setup_allowed_hosts(self.rab_allowed_hosts)

    @computed_field
    @property
    def database_uri(self) -> dict[str, str] | str:
        if self.in_build_step:
            return ""
        else:
            return database_url_from_env("DATABASE_CREDENTIALS")

    @computed_field
    @property
    def temporary_s3_bucket_configuration(self) -> dict[str, str]:
        if self.in_build_step:
            return {
                "bucket_name": "",
                "access_key_id": "",
                "secret_access_key": "",
            }
        else:
            return {
                "bucket_name": os.environ.get("TEMPORARY_S3_BUCKET_NAME", ""),
                "access_key_id": None,
                "secret_access_key": None,
            }

    @computed_field
    @property
    def permanent_s3_bucket_configuration(self) -> dict[str, str]:
        if self.in_build_step:
            return {
                "bucket_name": "",
                "access_key_id": "",
                "secret_access_key": "",
            }
        else:
            return {
                "bucket_name": os.environ.get("PERMANENT_S3_BUCKET_NAME", ""),
                "access_key_id": None,
                "secret_access_key": None,
            }

    @computed_field  # type: ignore[misc]
    @property
    def redis_url(self) -> str:
        if self.in_build_step:
            return ""

        return self.redis_endpoint


if "CIRCLECI" in os.environ:
    # CircleCI, don't validate
    # There's a funny issue with capitalisation here, so we casefold() everything in the environ so we can match it to
    # the properties in the settings models. Everything except for DATABASE_URL which is case sensitive.
    env = TestSettings.model_construct(
        **{key if key == "DATABASE_URL" else key.casefold(): value for key, value in os.environ.items()}
    )
elif os.environ.get("DJANGO_SETTINGS_MODULE", "") == "config.settings.local":
    # Local development
    env = LocalSettings()
elif os.environ.get("DJANGO_SETTINGS_MODULE", "") == "config.settings.test":
    # Testing
    env = TestSettings()  # type: ignore[call-arg]
elif "COPILOT_ENVIRONMENT_NAME" in os.environ:
    # Deployed on DBT Platform
    env = DBTPlatformSettings()
else:
    # Deployed on GOV.PaaS
    raise ValueError("Unknown environment")
