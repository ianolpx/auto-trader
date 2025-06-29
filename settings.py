from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


def get_secret(key_vault_name: str, key_name: str) -> tuple:
    credential = DefaultAzureCredential()
    key_client = SecretClient(
        vault_url=f"https://{key_vault_name}.vault.azure.net/",
        credential=credential
    )
    secret = key_client.get_secret(key_name)
    return secret.value


class Settings():
    app_version: str = "25.3.5"
    cosmos_api_key: str = get_secret("trader-k-v", "cosmos-api-key")
    cosmos_endpoint: str = get_secret("trader-k-v", "cosmos-endpoint")
    cosmos_database_id: str = "trader-db"
    cosmos_container_id: str = "Trader1"
    cosmos_partition_key: str = "T1"
    bybit_api_key: str = get_secret("trader-k-v", "bybit-api-key")
    bybit_secret_key: str = get_secret("trader-k-v", "bybit-secret-key")
    line_token: str = get_secret("trader-k-v", "line-token")
    target_period: str = get_secret("trader-k-v", "target-period")
    mailjet_api_key: str = get_secret("trader-k-v", "mailjet-api-key")
    mailjet_api_secret: str = get_secret("trader-k-v", "mailjet-api-secret")
    mailjet_sender_id: str = get_secret("trader-k-v", "mailjet-sender-id")
    mailjet_receiver_id: str = get_secret("trader-k-v", "mailjet-receiver-id")
    google_service_secret: str = get_secret(
        "trader-k-v",
        "google-service-secret")


settings = Settings()
import json

# python -m settings
if __name__ == "__main__":
    # print(settings.bybit_api_key)
    # print(settings.bybit_secret_key)
    # print(settings.target_period)
    # print(settings.google_service_secret)
    gss = json.loads(settings.google_service_secret)
    print(gss)
