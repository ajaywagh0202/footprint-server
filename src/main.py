from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from .database import Base, engine
# from .models.Master.division_master import DivisionMaster
# from .models.Master.station_master import StationMaster
# from .models.Master.user import User
# from .models.Master.zone_master import ZoneMaster
# from .models.Transaction.train_schedule import TrainSchedule
from .routers.master_route import division, station, user, zone
from .routers.transaction_route import train_schedule

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "Backend is running"}

app.include_router(zone.router)
app.include_router(division.router)
app.include_router(station.router)
app.include_router(train_schedule.router)
app.include_router(user.router)
