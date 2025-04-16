from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetSearchParams, PetUpdate


class CRUDPet(CRUDBase[Pet, PetCreate, PetUpdate]):
    async def search(
        self, db: AsyncSession, *, params: PetSearchParams, skip: int = 0, limit: int = 100
    ) -> List[Pet]:
        """
        Поиск питомцев с фильтрами.
        """
        conditions = []
        
        # Применяем фильтры
        if params.name:
            conditions.append(Pet.name.ilike(f"%{params.name}%"))
        if params.type:
            conditions.append(Pet.type.ilike(f"%{params.type}%"))
        if params.breed:
            conditions.append(Pet.breed.ilike(f"%{params.breed}%"))
        if params.color:
            conditions.append(Pet.color.ilike(f"%{params.color}%"))
        if params.min_age is not None:
            conditions.append(Pet.age >= params.min_age)
        if params.max_age is not None:
            conditions.append(Pet.age <= params.max_age)
        if params.is_available is not None:
            conditions.append(Pet.is_available == params.is_available)
        
        # Формируем запрос
        query = select(Pet)
        if conditions:
            query = query.where(and_(*conditions))
        
        # Добавляем пагинацию
        query = query.offset(skip).limit(limit)
        
        # Выполняем запрос
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id_or_name(self, db: AsyncSession, *, id: Optional[int] = None, name: Optional[str] = None) -> Optional[Pet]:
        """
        Получить питомца по ID или имени.
        """
        if id is None and name is None:
            return None
        
        conditions = []
        if id is not None:
            conditions.append(Pet.id == id)
        if name is not None:
            conditions.append(Pet.name.ilike(f"%{name}%"))
        
        query = select(Pet).where(or_(*conditions))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_unique_attributes(self, db: AsyncSession, *, name: str, type: str, breed: str) -> Optional[Pet]:
        """
        Получить питомца по комбинации уникальных атрибутов.
        """
        query = select(self.model).where(
            and_(
                self.model.name == name,
                self.model.type == type,
                self.model.breed == breed
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

pet = CRUDPet(Pet)