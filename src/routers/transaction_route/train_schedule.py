from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.Master.station_master import StationMaster
from ...models.Transaction.train_schedule import TrainSchedule
from ...schemas.transaction_schema.train_schedule import (
    TrainScheduleCreate,
    TrainScheduleGet,
    TrainScheduleUpdate,
)

router = APIRouter(prefix="/train-schedules", tags=["Train Schedules"])


def _commit(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record already exists or violates a database constraint",
        ) from exc


def _ensure_station(db: Session, station_id: UUID, detail: str = "Station not found"):
    if not db.query(StationMaster).filter(StationMaster.id == station_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _ensure_schedule_stations(db: Session, payload):
    if payload.station_uid:
        _ensure_station(db, payload.station_uid)
    if payload.from_station_uid:
        _ensure_station(db, payload.from_station_uid, "From station not found")
    if payload.to_station_uid:
        _ensure_station(db, payload.to_station_uid, "To station not found")


@router.post("/", response_model=TrainScheduleGet, status_code=status.HTTP_201_CREATED)
def create_train_schedule(payload: TrainScheduleCreate, db: Session = Depends(get_db)):
    _ensure_schedule_stations(db, payload)
    schedule = TrainSchedule(**payload.model_dump())
    db.add(schedule)
    _commit(db)
    db.refresh(schedule)
    return schedule


@router.get("/", response_model=list[TrainScheduleGet])
def get_train_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TrainSchedule).offset(skip).limit(limit).all()


@router.get("/{schedule_id}", response_model=TrainScheduleGet)
def get_train_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    schedule = db.query(TrainSchedule).filter(TrainSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train schedule not found")
    return schedule


@router.put("/{schedule_id}", response_model=TrainScheduleGet)
def update_train_schedule(
    schedule_id: UUID,
    payload: TrainScheduleUpdate,
    db: Session = Depends(get_db),
):
    schedule = db.query(TrainSchedule).filter(TrainSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train schedule not found")

    _ensure_schedule_stations(db, payload)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    _commit(db)
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_train_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    schedule = db.query(TrainSchedule).filter(TrainSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train schedule not found")

    db.delete(schedule)
    _commit(db)
    return None
