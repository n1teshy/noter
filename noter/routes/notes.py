from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from noter.models.db.meta import get_session
from noter.models.db.note import Note
from noter.models.val.note import NoteCreate, NoteJSON, ensure_constraints
from noter.utils.auth import AuthUser, require_auth

router = APIRouter()


@router.get("/", response_model=list[NoteJSON])
async def get_notes(
    only_public: bool = False,
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    stmt = (
        select(Note)
        .options(selectinload(Note.author))
        .offset(skip)
        .limit(limit)
    )
    if only_public:
        stmt = stmt.where(Note.is_public.is_(True))
    else:
        stmt = stmt.where(Note.author_id == user.id)
    notes = await session.execute(stmt)
    return [note.to_json() for note in notes.scalars().all()]


@router.post("/", response_model=NoteJSON)
async def add_note(
    data: NoteCreate,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_constraints(data, session)
    note = Note.from_data(data.model_dump(), author_id=user.id)
    session.add(note)
    await session.commit()
    stmt = (
        select(Note)
        .options(selectinload(Note.author))
        .where(Note.id == note.id)
    )
    note = (await session.execute(stmt)).scalar_one()
    return note.to_json()
