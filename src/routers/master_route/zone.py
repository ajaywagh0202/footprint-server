from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.Master.division_master import DivisionMaster
from ...models.Master.zone_master import ZoneMaster
from ...schemas.master_schema.division_master import DivisionGet
from ...schemas.master_schema.zone_master import ZoneCreate, ZoneGet, ZoneUpdate

router = APIRouter(prefix="/zones", tags=["Zones"])


def _commit(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record already exists or violates a database constraint",
        ) from exc


@router.post("/", response_model=ZoneGet, status_code=status.HTTP_201_CREATED)
def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)):
    zone = ZoneMaster(**payload.model_dump())
    db.add(zone)
    _commit(db)
    db.refresh(zone)
    return zone


@router.get("/", response_model=list[ZoneGet])
def get_zones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ZoneMaster).offset(skip).limit(limit).all()


@router.get("/{zone_id}", response_model=ZoneGet)
def get_zone(zone_id: UUID, db: Session = Depends(get_db)):
    zone = db.query(ZoneMaster).filter(ZoneMaster.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.get("/{zone_id}/divisions", response_model=list[DivisionGet])
def get_zone_divisions(zone_id: UUID, db: Session = Depends(get_db)):
    zone = db.query(ZoneMaster).filter(ZoneMaster.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return db.query(DivisionMaster).filter(DivisionMaster.zone_id == zone_id).all()


@router.put("/{zone_id}", response_model=ZoneGet)
def update_zone(zone_id: UUID, payload: ZoneUpdate, db: Session = Depends(get_db)):
    zone = db.query(ZoneMaster).filter(ZoneMaster.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(zone, key, value)

    _commit(db)
    db.refresh(zone)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(zone_id: UUID, db: Session = Depends(get_db)):
    zone = db.query(ZoneMaster).filter(ZoneMaster.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    db.delete(zone)
    _commit(db)
    return None
