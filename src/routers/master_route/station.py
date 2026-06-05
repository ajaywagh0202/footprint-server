from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.Master.division_master import DivisionMaster
from ...models.Master.station_master import StationMaster
from ...models.Master.zone_master import ZoneMaster
from ...models.Transaction.train_schedule import TrainSchedule
from ...schemas.master_schema.station_master import (
    StationCreate,
    StationGet,
    StationUpdate,
    StationWithDivisionZone,
)
from ...schemas.transaction_schema.train_schedule import TrainScheduleGet

router = APIRouter(prefix="/stations", tags=["Stations"])


def _commit(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record already exists or violates a database constraint",
        ) from exc


def _ensure_division(db: Session, division_code: str):
    if not db.query(DivisionMaster).filter(DivisionMaster.division_code == division_code).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")


@router.post("/", response_model=StationGet, status_code=status.HTTP_201_CREATED)
def create_station(payload: StationCreate, db: Session = Depends(get_db)):
    _ensure_division(db, payload.division_code)
    station = StationMaster(**payload.model_dump())
    db.add(station)
    _commit(db)
    db.refresh(station)
    return station


@router.get("/", response_model=list[StationWithDivisionZone])
def get_stations(db: Session = Depends(get_db)):
    rows = (
        db.query(
            StationMaster,
            DivisionMaster.division.label("division_name"),
            DivisionMaster.division_code.label("division_code"),
            ZoneMaster.zone.label("zone_name"),
            ZoneMaster.zone_code.label("zone_code"),
        )
        .join(DivisionMaster, StationMaster.division_code == DivisionMaster.division_code)
        .join(ZoneMaster, DivisionMaster.zone_code == ZoneMaster.zone_code)
        .all()
    )

    return [
        {
            **StationGet.model_validate(station).model_dump(),
            "division_name": division_name,
            "division_code": division_code,
            "zone_name": zone_name,
            "zone_code": zone_code,
        }
        for station, division_name, division_code, zone_name, zone_code in rows
    ]


@router.get("/{station_id}", response_model=StationGet)
def get_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return station


@router.get("/{station_id}/train-schedules", response_model=list[TrainScheduleGet])
def get_station_train_schedules(station_id: int, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return db.query(TrainSchedule).filter(TrainSchedule.station_code == station.station_code).all()


@router.put("/{station_id}", response_model=StationGet)
def update_station(station_id: int, payload: StationUpdate, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

    data = payload.model_dump(exclude_unset=True)
    if data.get("division_code"):
        _ensure_division(db, data["division_code"])

    for key, value in data.items():
        setattr(station, key, value)

    _commit(db)
    db.refresh(station)
    return station


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

    db.delete(station)
    _commit(db)
    return None
