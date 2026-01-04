from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from noter.models.db.meta import get_session
from noter.models.db.note import Note
from noter.models.val.note import NoteCreate, NoteJSON, ensure_constraints

router = APIRouter()


@router.get("/", response_model=list[NoteJSON])
async def get_notes(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Note).offset(skip).limit(limit)
    notes = await session.execute(stmt)
    return [note.to_json() for note in notes.scalars().all()]


@router.post("/", response_model=NoteJSON)
async def add_note(
    data: NoteCreate, session: AsyncSession = Depends(get_session)
):
    await ensure_constraints(data, session)
    note = Note.from_data(data.model_dump())
    session.add(note)
    await session.commit()
    return note.to_json()
