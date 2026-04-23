from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.schemas.category import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db
from app.db_depends import get_async_db

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """Возвращает список всех категорий."""
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    categories = await db.scalars(stmt)
    return categories.all()


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate, db: AsyncSession = Depends(get_async_db)
):
    """Создает новую категорию."""
    # Проверка существования parent_id
    if category.parent_id is not None:
        stmt = (
            select(CategoryModel)
            .where(
                CategoryModel.id == category.parent_id, CategoryModel.is_active == True
            )
            .order_by(CategoryModel.id.desc())
        )
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Обновляет категорию по её ID."""
    # Проверка существования категории
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    result = await db.scalars(stmt)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(
            CategoryModel.id == category.parent_id, CategoryModel.is_active == True
        )
        result_parent = await db.scalars(parent_stmt)
        parent = result_parent.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
        # Обновление категории
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump())
    )
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """Удаляет категорию по её ID."""
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True,
    )
    category = await db.scalars(stmt)
    if category.first() is None:
        raise HTTPException(status_code=404, detail="Category not found")
    # category.is_active = False
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    await db.commit()

    return {"status": "success", "message": "Category marked as inactive"}
