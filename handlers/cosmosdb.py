from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions
from azure.cosmos.partition_key import PartitionKey
import asyncio
from settings import settings


class CosmosDBHandler():
    endpoint = settings.cosmos_endpoint
    key = settings.cosmos_api_key
    database_id = settings.cosmos_database_id
    container_id = settings.cosmos_container_id
    partition_key = settings.cosmos_partition_key

    client = None
    container = None

    async def get_or_create_container(self):
        self.client = CosmosClient(self.endpoint, credential=self.key)
        database = await self.client.create_database_if_not_exists(
                id=self.database_id
            )
        container = await database.create_container_if_not_exists(
                id=self.container_id,
                partition_key=PartitionKey(path=self.partition_key)
            )
        return container

    async def get_profile(self, container):
        items = []
        async for item in container.query_items(
            query="SELECT * FROM c WHERE c.T1 = 'bybit'",
            partition_key=None
        ):
            items.append(item)
        if len(items) == 1:
            return items[0]
        return items

    async def update_profile(self, item: dict, container):
        try:
            await container.upsert_item(body=item)
        except exceptions.CosmosHttpResponseError as e:
            print(f'Error: {e}')
            return False

    async def close(self):
        await self.client.close()


async def test():
    db = CosmosDBHandler()
    container = await db.get_or_create_container()
    a = await db.get_profile(container)
    print(a)
    await db.update_profile({
        'status': 'ready',  # ready, bought - 2 modes
        'id': '1',
        'T1': 'bybit'
        }, container)
    await db.close()

if __name__ == "__main__":
    asyncio.run(test())
