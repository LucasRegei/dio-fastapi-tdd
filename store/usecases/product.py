from typing import List
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import NotFoundException, ValidationError


class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        product_model = ProductModel(**body.model_dump())

        # Inserindo o documento no MongoDB
        insert_result = await self.collection.insert_one(product_model.model_dump())

        # Recuperando o documento inserido para garantir que esta retornando o documento correto
        inserted_product = await self.collection.find_one(
            {"_id": insert_result.inserted_id}
        )

        if not inserted_product:
            raise ValidationError("Failed to retrieve the inserted product.")

        return ProductOut(**inserted_product)

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return ProductOut(**result)

    async def query(self) -> List[ProductOut]:
        return [ProductOut(**item) async for item in self.collection.find()]

    # Caso de uso que filtra por range de preços. Solicitado pelo desafio.
    async def query_by_price(
        self, min_price: float, max_price: float
    ) -> List[ProductOut]:
        cursor = self.collection.find({"price": {"$gt": min_price, "$lt": max_price}})
        products = await cursor.to_list(length=None)
        return [ProductOut(**item) for item in products]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": body.model_dump(exclude_none=True)},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        # Adicionado a excessão
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        product = await self.collection.find_one({"id": id})
        if not product:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        result = await self.collection.delete_one({"id": id})

        return True if result.deleted_count > 0 else False


product_usecase = ProductUsecase()
