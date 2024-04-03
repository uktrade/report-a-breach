import os
from typing import Any

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

    clam_av_username: str | None = None
    clam_av_password: str | None = None
    clam_av_domain: str | None = None

    company_house_api_key: str | None = None

    gov_notify_api_key: str = None
    email_verify_code_template_id: str
    restrict_sending: bool = True
    email_verify_timeout_seconds: int = 3600

    sentry_dsn: str | None = None
    sentry_environment: str | None = None

    gtm_enabled: bool = False
    gtm_id: str | None = None

    aws_storage_bucket_name: str | None = None
    aws_endpoint_url: str | None = None
    aws_s3_url_protocol: str = "https:"
    aws_region: str | None = None

    @computed_field
    @property
    def aws_access_key_id(self) -> str:
        return self.s3_bucket_config["access_key_id"]

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        return self.rab_allowed_hosts

    @computed_field
    @property
    def database_uri(self) -> str:
        return self.database_url


class LocalSettings(BaseSettings):
    database_url: str | None = None

    @computed_field
    @property
    def database_uri(self) -> str:
        return self.database_url


class GovPaasSettings(BaseSettings):
    class VCAPServices(BaseModel):
        model_config = ConfigDict(extra="ignore")

        postgres: list[dict[str, Any]]
        redis: list[dict[str, Any]]
        aws_s3_bucket: list[dict[str, Any]] = Field(alias="aws-s3-bucket")

    vcap_services: VCAPServices | None = VCAPServices

    @computed_field
    @property
    def database_uri(self) -> dict:
        return self.vcap_services.postgres[0]["credentials"]["uri"]

    @computed_field
    @property
    def s3_bucket_config(self) -> dict:
        return self.vcap_services.aws_s3_bucket[0]["credentials"]


class DBTPlatformSettings(BaseSettings):
    in_build_step: bool = Field(alias="BUILD_STEP", default=False)

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        if self.in_build_step:
            return self.RAB_ALLOWED_HOSTS
        else:
            return setup_allowed_hosts(self.RAB_ALLOWED_HOSTS)


if "config.settings.local" in os.environ.get("DJANGO_SETTINGS_MODULE", ""):
    # Local development
    env = LocalSettings()
elif "COPILOT_ENVIRONMENT_NAME" in os.environ:
    # Deployed on DBT Platform
    env = DBTPlatformSettings()
else:
    # Deployed on GOV.PaaS
    env = GovPaasSettings()
