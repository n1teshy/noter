from fastapi import APIRouter, Depends, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from noter.models.db.meta import get_session
from noter.models.db.note import Note
from noter.models.val.note import (
    NoteCreate,
    NoteJSON,
    ensure_constraints,
    ensure_exists,
    ensure_ownership,
    ensure_viewership,
)
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
    notes = (await session.execute(stmt)).scalars().all()
    return [note.to_json() for note in notes]


@router.post("/", response_model=NoteJSON)
async def add_note(
    data: NoteCreate,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_constraints(data, session, user.id)
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


@router.get("/{note_id}/", response_model=NoteJSON)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_exists(session, note_id)
    await ensure_viewership(session, user.id, note_id)
    note: Note = await session.get(
        Note,
        note_id,
        options=(selectinload(Note.author),),
    )
    return note.to_json()


@router.put("/{note_id}/", response_model=NoteJSON)
async def update_note(
    note_id: int,
    data: NoteCreate,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_exists(session, note_id)
    await ensure_ownership(session, user.id, note_id)
    await ensure_constraints(data, session, user.id, note_id)
    note: Note = await session.get(
        Note,
        note_id,
        options=(selectinload(Note.author),),
    )
    note.update(data.model_dump())
    await session.commit()
    return note.to_json()


@router.delete("/{note_id}/", response_model=NoteJSON)
async def delete_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_exists(session, note_id)
    await ensure_ownership(session, user.id, note_id)
    stmt = delete(Note).where(Note.id == note_id)
    await session.execute(stmt)
    await session.commit()
    return Response(status_code=200)
