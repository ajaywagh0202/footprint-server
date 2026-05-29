from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.Master.division_master import DivisionMaster
from ...models.Master.station_master import StationMaster
from ...models.Transaction.train_schedule import TrainSchedule
from ...schemas.master_schema.station_master import StationCreate, StationGet, StationUpdate
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


def _ensure_division(db: Session, division_id: UUID):
    if not db.query(DivisionMaster).filter(DivisionMaster.id == division_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")


@router.post("/", response_model=StationGet, status_code=status.HTTP_201_CREATED)
def create_station(payload: StationCreate, db: Session = Depends(get_db)):
    _ensure_division(db, payload.division_id)
    station = StationMaster(**payload.model_dump())
    db.add(station)
    _commit(db)
    db.refresh(station)
    return station


@router.get("/", response_model=list[StationGet])
def get_stations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(StationMaster).offset(skip).limit(limit).all()


@router.get("/{station_id}", response_model=StationGet)
def get_station(station_id: UUID, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return station


@router.get("/{station_id}/train-schedules", response_model=list[TrainScheduleGet])
def get_station_train_schedules(station_id: UUID, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return db.query(TrainSchedule).filter(TrainSchedule.station_uid == station_id).all()


@router.put("/{station_id}", response_model=StationGet)
def update_station(station_id: UUID, payload: StationUpdate, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

    data = payload.model_dump(exclude_unset=True)
    if data.get("division_id"):
        _ensure_division(db, data["division_id"])

    for key, value in data.items():
        setattr(station, key, value)

    _commit(db)
    db.refresh(station)
    return station


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(station_id: UUID, db: Session = Depends(get_db)):
    station = db.query(StationMaster).filter(StationMaster.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

    db.delete(station)
    _commit(db)
    return None
