from fastapi import APIRouter
from uris.post_couriers import post_couriers_route
from uris.patch_couriers import patch_couriers_route
from uris.post_orders import post_orders_route
from uris.post_orders_assign import post_orders_assign_route
from uris.post_orders_complete import post_orders_complete_route
from uris.get_courier import get_couriers_route

router = APIRouter()

router.include_router(post_couriers_route)
router.include_router(patch_couriers_route)
router.include_router(post_orders_route)
router.include_router(post_orders_assign_route)
router.include_router(post_orders_complete_route)
router.include_router(get_couriers_route)
