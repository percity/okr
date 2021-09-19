# -*- coding: utf-8 -*-
# Part of Sentilis. See LICENSE file for full copyright and licensing details.
from tona.core import Config, get_config
from starlette.responses import JSONResponse
from tona.utils.exceptions import TonaException
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Response, Header, Depends
from .models.time_entry import TimeEntryStart, TimeEntryStop, TimeEntryAnlyzeMeta
from .models.time_entry import TimeEntryEdit, TimeEntryItems, TimeEntryItem, TimeEntryAnlyzeItems
from .services.entry import Entry
from .services.analyze import Analyze
from peewee import DoesNotExist
from tona.utils import logger

v1 = APIRouter()
entryService = Entry()
analyzeService = Analyze()

@v1.post('/entries/start', response_model=TimeEntryItem, status_code=status.HTTP_201_CREATED)
async def post_entries_start(entry: TimeEntryStart):
    try:
        res = TimeEntryItem()
        res.payload = entryService.start(entry.dict(exclude_none=True))
        return res
    except TonaException as e:
        logger.exception(e)
        raise HTTPException(status_code=e.code, detail=e.detail)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))

@v1.post('/entries/stop', response_model=TimeEntryItem, status_code=status.HTTP_202_ACCEPTED)
async def post_entries_stop(entry: TimeEntryStop):
    try:
        res = TimeEntryItem()
        res.payload = entryService.stop(entry.id, entry.dict())
        return res
    except DoesNotExist as e:
        logger.exception(e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))

@v1.get('/entries/current', response_model=TimeEntryItem)
async def get_entries_current():
    res = TimeEntryItem()
    res.payload = entryService.current()
    if res.payload:
        return res
    raise HTTPException(status_code=404, detail="Not found current entry")


@v1.put('/entries/{entry_id}', response_model=TimeEntryItem, status_code=status.HTTP_202_ACCEPTED)
def put_entries(entry_id: int, entry: TimeEntryEdit):
    try:
        data: dict = entry.dict(exclude={"id": ...}, exclude_none=True, exclude_defaults=True)
        if len(data.keys()):
            res = TimeEntryItem()
            res.payload = entryService.edit(entry_id, data)
            return res
        else:
            raise TonaException(status.HTTP_400_BAD_REQUEST,
                                "Required min 1 item at the body")
    except TonaException as e:
        logger.exception(e)
        raise HTTPException(status_code=e.code, detail=e.detail)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Entry not found")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

@v1.get('/entries', response_model=TimeEntryItems, response_model_exclude_none=None)
def get_entries(skip: int = 0, limit: int = 100, sort_by: str = "-created_at"):
    res = TimeEntryItems()
    res.payload = entryService.filter(locals())
    return res


@v1.delete('/entries/{entry_id}', response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
def delete_entries(entry_id: int):
    try:
        entryService.remove(entry_id)
        return JSONResponse()
    except TonaException as e:
        logger.exception(e)
        raise HTTPException(status_code=e.code, detail=e.detail)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Entry not found")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@v1.get("/analyze", response_model=TimeEntryAnlyzeItems, response_model_exclude_none=None)
def get_analyze(skip: int = 0, limit: int = 100, group_by: str = "any", group_id: int = 0,
                export: str = "", sort_by: str = "-created_at",  filters: str = "",
                tz: Optional[str] = Header("UTC")):

    res = TimeEntryAnlyzeItems()
    if group_by == 'any':
        res.payload = analyzeService.group_by_any(locals())
    
    if export.lower() == 'pdf':
        fpdf = analyzeService.export_pdf(group_by, res.payload, tz)
        meta = TimeEntryAnlyzeMeta()
        meta.slug = "export-to"
        meta.value = fpdf.get("name")
        res.meta = [meta]
    elif export.lower() == 'csv':
        fpdf = analyzeService.export_csv(group_by, res.payload, tz)
        meta = TimeEntryAnlyzeMeta()
        meta.slug = "export-to"
        meta.value = fpdf.get("name")
        res.meta = [meta]
    return res
