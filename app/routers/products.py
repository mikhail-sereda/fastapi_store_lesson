from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, exists, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas.product import Product as ProductSchema, ProductCreate
from app.db_depends import get_db
from app.db_depends import get_async_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """Возвращает список всех товаров."""
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    result = await db.scalars(stmt)
    products = result.all()

    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate, db: AsyncSession = Depends(get_async_db)
):
    """Создаёт новый товар."""
    # проверка на существование категории
    # stmt_categories = select(CategoryModel).where(
    #     CategoryModel.id == product.category_id, CategoryModel.is_active == True
    # )
    stmt_categories = select(
        exists().where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True,
        )
    )
    category = await db.scalar(stmt_categories)
    if not category:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get(
    "/category/{category_id}",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int, db: AsyncSession = Depends(get_async_db)
):
    """Возвращает список товаров в указанной категории по её ID."""
    stmt_category = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    result = await db.scalars(stmt_category)
    category = result.first()

    # проверка существования и активности категории товара
    if not category:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    stmt = select(ProductModel).where(
        ProductModel.category_id == category_id, ProductModel.is_active == True
    )
    result_products = await db.scalars(stmt)
    products = result_products.all()

    return products


@router.get(
    "/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """Возвращает детальную информацию о товаре по его ID."""
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    product = result.first()

    # Проверка существования и активности товара
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    # проверка существования и активности категории товара
    stmt_category = select(CategoryModel).where(
        CategoryModel.id == product.category_id, CategoryModel.is_active == True
    )
    result_category = await db.scalars(stmt_category)
    category = result_category.first()

    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    return product


@router.put(
    "/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK
)
async def update_product(
    product_id: int,
    product_update: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Обновляет товар по его ID."""
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active == True
    )
    result_product = await db.scalars(stmt)
    product_db = result_product.first()

    # Проверка существования и активности товара
    if product_db is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    # проверка существования и активности категории обновленного товара
    stmt_category = select(CategoryModel).where(
        CategoryModel.id == product_update.category_id, CategoryModel.is_active == True
    )
    result = await db.scalars(stmt_category)
    category = result.first()

    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    for field, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product_db, field, value)

    await db.commit()
    await db.refresh(product_db)
    return product_db


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """Удаляет товар по его ID."""

    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    product_db = result.first()

    # Проверка существования и активности товара
    if product_db is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    product_db.is_active = False
    await db.commit()

    return {"status": "success", "message": "Product marked as inactive"}
