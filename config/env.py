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
    email_verify_code_template_id: str
    restrict_sending: bool = True
    email_verify_timeout_seconds: int = 3600

    sentry_dsn: str = ""
    sentry_environment: str = ""

    gtm_enabled: bool = True
    gtm_id: str = ""

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_endpoint_url: str = ""
    aws_default_region: str = "eu-west-2"
    temporary_s3_bucket_name: str = "temporary-document-bucket"
    permanent_s3_bucket_name: str = "permanent-document-bucket"
    pre_signed_url_expiry_seconds: int = 3600

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        return self.rab_allowed_hosts


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


class DBTPlatformSettings(BaseSettings):
    in_build_step: bool = Field(alias="BUILD_STEP", default=False)

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        if self.in_build_step:
            return self.RAB_ALLOWED_HOSTS
        else:
            return setup_allowed_hosts(self.RAB_ALLOWED_HOSTS)

    @computed_field
    @property
    def database_uri(self) -> dict:
        return database_url_from_env("DATABASE_CREDENTIALS")


if "config.settings.local" in os.environ.get("DJANGO_SETTINGS_MODULE", ""):
    # Local development
    env = LocalSettings()
elif "COPILOT_ENVIRONMENT_NAME" in os.environ:
    # Deployed on DBT Platform
    env = DBTPlatformSettings()
else:
    # Deployed on GOV.PaaS
    env = GovPaasSettings()
