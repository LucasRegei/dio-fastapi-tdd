from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4
from store.core.exceptions import NotFoundException, ValidationError

from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase

router = APIRouter(tags=["products"])


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.create(body=body)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()
        )


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query()


# Rota criada para solicitar todos os documentos dentro do range definido pelo price.
@router.get(path="/{min_price}/{max_price}", status_code=status.HTTP_200_OK)
async def query_by_price(
    min_price: float = Path(alias="min_price", description="Minimum price"),
    max_price: float = Path(alias="max_price", description="Maximum price"),
    usecase: ProductUsecase = Depends(),
) -> List[ProductOut]:
    return await usecase.query_by_price(min_price, max_price)


@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    try:  # Adicionado o tratamento de excessão
        await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    return await usecase.update(id=id, body=body)


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
