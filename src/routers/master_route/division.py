from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.Master.division_master import DivisionMaster
from ...models.Master.station_master import StationMaster
from ...models.Master.zone_master import ZoneMaster
from ...schemas.master_schema.division_master import (
    DivisionCreate,
    DivisionGet,
    DivisionUpdate,
    DivisionWithZone,
)
from ...schemas.master_schema.station_master import StationGet

router = APIRouter(prefix="/divisions", tags=["Divisions"])


def _commit(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record already exists or violates a database constraint",
        ) from exc


def _ensure_zone(db: Session, zone_id: UUID):
    if not db.query(ZoneMaster).filter(ZoneMaster.id == zone_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")


@router.post("/", response_model=DivisionGet, status_code=status.HTTP_201_CREATED)
def create_division(payload: DivisionCreate, db: Session = Depends(get_db)):
    _ensure_zone(db, payload.zone_id)
    division = DivisionMaster(**payload.model_dump())
    db.add(division)
    _commit(db)
    db.refresh(division)
    return division


@router.get("/", response_model=list[DivisionWithZone])
def get_divisions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rows = (
        db.query(
            DivisionMaster,
            ZoneMaster.zone.label("zone_name"),
            ZoneMaster.zone_code.label("zone_code"),
        )
        .join(ZoneMaster, DivisionMaster.zone_id == ZoneMaster.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            **DivisionGet.model_validate(division).model_dump(),
            "zone_name": zone_name,
            "zone_code": zone_code,
        }
        for division, zone_name, zone_code in rows
    ]


@router.get("/{division_id}", response_model=DivisionGet)
def get_division(division_id: UUID, db: Session = Depends(get_db)):
    division = db.query(DivisionMaster).filter(DivisionMaster.id == division_id).first()
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    return division


@router.get("/{division_id}/stations", response_model=list[StationGet])
def get_division_stations(division_id: UUID, db: Session = Depends(get_db)):
    division = db.query(DivisionMaster).filter(DivisionMaster.id == division_id).first()
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    return db.query(StationMaster).filter(StationMaster.division_id == division_id).all()


@router.put("/{division_id}", response_model=DivisionGet)
def update_division(division_id: UUID, payload: DivisionUpdate, db: Session = Depends(get_db)):
    division = db.query(DivisionMaster).filter(DivisionMaster.id == division_id).first()
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")

    data = payload.model_dump(exclude_unset=True)
    if data.get("zone_id"):
        _ensure_zone(db, data["zone_id"])

    for key, value in data.items():
        setattr(division, key, value)

    _commit(db)
    db.refresh(division)
    return division


@router.delete("/{division_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_division(division_id: UUID, db: Session = Depends(get_db)):
    division = db.query(DivisionMaster).filter(DivisionMaster.id == division_id).first()
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")

    db.delete(division)
    _commit(db)
    return None
