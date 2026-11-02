"""
KindBite — API v1 Router
Aggregates all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    restaurants,
    sales,
    preparations,
    predictions,
    donations,
    ngos,
    matching,
    deliveries,
    volunteers,
    admin,
    ml,
    notifications,
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
router.include_router(sales.router, prefix="/sales", tags=["Sales"])
router.include_router(preparations.router, prefix="/preparations", tags=["Preparations"])
router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
router.include_router(donations.router, prefix="/donations", tags=["Donations"])
router.include_router(ngos.router, prefix="/ngos", tags=["NGOs"])
router.include_router(matching.router, prefix="/matching", tags=["Matching"])
router.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])
router.include_router(volunteers.router, prefix="/volunteers", tags=["Volunteers"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
router.include_router(ml.router, prefix="/ml", tags=["ML"])
router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
