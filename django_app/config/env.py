import os
from typing import Any

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.network import setup_allowed_hosts
from pydantic import BaseModel, ConfigDict, Field, computed_field
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

    company_house_api_key: str | None = None

    gov_notify_api_key: str = None
    email_verify_code_template_id: str = ""
    email_verify_code_template_id: str
    restrict_sending: bool = True
    email_verify_timeout_seconds: int = 3600

    sentry_dsn: str = ""
    sentry_environment: str = ""

    gtm_enabled: bool = True
    gtm_id: str = ""

    temporary_s3_bucket_access_key_id: str = "test"
    temporary_s3_bucket_secret_access_key: str = "test"

    permanent_s3_bucket_access_key_id: str = "test"
    permanent_s3_bucket_secret_access_key: str = "test"

    aws_endpoint_url: str = ""
    aws_default_region: str = "eu-west-2"
    temporary_s3_bucket_name: str = "temporary-document-bucket"
    permanent_s3_bucket_name: str = "permanent-document-bucket"
    presigned_url_expiry_seconds: int = 3600

    # Django sites
    report_a_suspected_breach_domain: str = "report-a-suspected-breach"
    view_a_suspected_breach_domain: str = "view-a-suspected-breach"

    # SSO
    enforce_staff_sso: bool = False
    authbroker_url: str = ""
    authbroker_client_id: str = ""
    authbroker_client_secret: str = ""
    authbroker_token_session_key: str = ""
    authbroker_staff_sso_scope: str = ""

    mock_sso_token: str = ""
    mock_sso_scope: str = ""
    mock_sso_username: str = ""
    mock_sso_email_user_id: str = ""
    oauthlib_insecure_transport: int = 0

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        return self.rab_allowed_hosts

    @computed_field
    @property
    def temporary_s3_bucket_configuration(self) -> dict:
        return {
            "bucket_name": self.temporary_s3_bucket_name,
            "access_key_id": self.temporary_s3_bucket_access_key_id,
            "secret_access_key": self.temporary_s3_bucket_secret_access_key,
        }

    @computed_field
    @property
    def permanent_s3_bucket_configuration(self) -> dict:
        return {
            "bucket_name": self.permanent_s3_bucket_name,
            "access_key_id": self.permanent_s3_bucket_access_key_id,
            "secret_access_key": self.permanent_s3_bucket_secret_access_key,
        }


class LocalSettings(BaseSettings):
    database_uri: str = Field(alias="DATABASE_URL")


class GovPaasSettings(BaseSettings):
    class VCAPServices(BaseModel):
        model_config = ConfigDict(extra="ignore")

        postgres: list[dict[str, Any]]
        aws_s3_bucket: list[dict[str, Any]] = Field(alias="aws-s3-bucket")

    vcap_services: VCAPServices | None = VCAPServices

    @computed_field
    @property
    def database_uri(self) -> dict:
        return self.vcap_services.postgres[0]["credentials"]["uri"]

    @property
    def get_temporary_bucket_vcap(self) -> dict:
        return next((each["credentials"] for each in self.vcap_services.aws_s3_bucket if "temporary" in each["name"]), {})

    @property
    def get_permanent_bucket_vcap(self) -> dict:
        return next((each["credentials"] for each in self.vcap_services.aws_s3_bucket if "permanent" in each["name"]), {})

    @computed_field
    @property
    def temporary_s3_bucket_configuration(self) -> dict:
        return {
            "bucket_name": self.get_temporary_bucket_vcap["bucket_name"],
            "access_key_id": self.get_temporary_bucket_vcap["aws_access_key_id"],
            "secret_access_key": self.get_temporary_bucket_vcap["aws_secret_access_key"],
        }

    @computed_field
    @property
    def permanent_s3_bucket_configuration(self) -> dict:
        return {
            "bucket_name": self.get_permanent_bucket_vcap["bucket_name"],
            "access_key_id": self.get_permanent_bucket_vcap["aws_access_key_id"],
            "secret_access_key": self.get_permanent_bucket_vcap["aws_secret_access_key"],
        }


class DBTPlatformSettings(BaseSettings):
    in_build_step: bool = Field(alias="BUILD_STEP", default=False)

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        if self.in_build_step:
            return self.rab_allowed_hosts
        else:
            return setup_allowed_hosts(self.rab_allowed_hosts)

    @computed_field
    @property
    def database_uri(self) -> dict:
        return database_url_from_env("DATABASE_CREDENTIALS")


if os.environ.get("DJANGO_SETTINGS_MODULE", "") in ["config.settings.local", "config.settings.test"]:
    # Local development
    env = LocalSettings()
elif "COPILOT_ENVIRONMENT_NAME" in os.environ:
    # Deployed on DBT Platform
    env = DBTPlatformSettings()
else:
    # Deployed on GOV.PaaS
    env = GovPaasSettings()
