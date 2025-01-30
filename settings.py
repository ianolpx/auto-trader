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
    app_version: str = "0.0.4"
    cosmos_api_key: str = get_secret("trader-k-v", "cosmos-api-key")
    cosmos_endpoint: str = get_secret("trader-k-v", "cosmos-endpoint")
    cosmos_database_id: str = "trader-db"
    cosmos_container_id: str = "Trader1"
    cosmos_partition_key: str = "T1"
    bybit_api_key: str = get_secret("trader-k-v", "bybit-api-key")
    bybit_secret_key: str = get_secret("trader-k-v", "bybit-secret-key")
    line_token: str = get_secret("trader-k-v", "line-token")
    target_period: str = get_secret("trader-k-v", "target-period")


settings = Settings()

# python -m settings
if __name__ == "__main__":
    print(settings.bybit_api_key)
    print(settings.bybit_secret_key)
    print(settings.cosmos_api_key)
