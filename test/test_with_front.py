from fastapi import APIRouter, Request
from email_validator import validate_email
from datetime import datetime, timedelta
import pymongo


router = APIRouter()


@router.get('/')
async def test_get(request: Request):
    client_host = request.client.host
    return {"client_host": client_host}