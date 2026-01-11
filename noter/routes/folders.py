from fastapi import APIRouter, Depends, Response
from sqlalchemy import delete, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import noter.utils.constants as c
from noter.models.db.folder import Folder
from noter.models.db.meta import get_session
from noter.models.db.meta.folder_note import FolderNote
from noter.models.db.note import Note
from noter.models.val.folder import (
    FolderCreate,
    FolderJSON,
    ensure_constraints,
    ensure_exists,
    ensure_ownership,
)
from noter.models.val.note import NoteJSON
from noter.utils.auth import AuthUser, require_auth
from noter.utils.exceptions import AppException

router = APIRouter()


@router.get("/", response_model=list[FolderJSON])
async def get_folders(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    stmt = (
        select(Folder)
        .options(selectinload(Folder.author))
        .where(Folder.author_id == user.id)
        .offset(skip)
        .limit(limit)
    )
    folders = (await session.execute(stmt)).scalars().all()
    return [folder.to_json() for folder in folders]


@router.post("/", response_model=FolderJSON)
async def add_folder(
    data: FolderCreate,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_constraints(data, session, user.id)
    folder = Folder.from_data(data.model_dump(), author_id=user.id)
    session.add(folder)
    await session.commit()
    stmt = (
        select(Folder)
        .options(selectinload(Folder.author))
        .where(Folder.id == folder.id)
    )
    folder = (await session.execute(stmt)).scalar_one()
    return folder.to_json()


@router.get("/{folder_id}/", response_model=FolderJSON)
async def get_folder(
    folder_id: int,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_exists(session, folder_id)
    await ensure_ownership(session, user.id, folder_id)
    folder: Folder = await session.get(
        Folder,
        folder_id,
        options=(selectinload(Folder.author),),
    )
    return folder.to_json()


@router.put("/{folder_id}/", response_model=FolderJSON)
async def update_folder(
    folder_id: int,
    data: FolderCreate,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_exists(session, folder_id)
    await ensure_ownership(session, user.id, folder_id)
    await ensure_constraints(data, session, user.id, folder_id)
    folder: Folder = await session.get(
        Folder,
        folder_id,
        options=(selectinload(Folder.author),),
    )
    folder.update(data.model_dump())
    await session.commit()
    return folder.to_json()


@router.delete("/{folder_id}/", response_model=FolderJSON)
async def delete_folder(
    folder_id: int,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_exists(session, folder_id)
    await ensure_ownership(session, user.id, folder_id)
    stmt = delete(Folder).where(Folder.id == folder_id)
    await session.execute(stmt)
    return Response(status_code=200)


@router.get("/{folder_id}/notes/", response_model=list[NoteJSON])
async def get_notes_from_folder(
    folder_id: int,
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_ownership(session, user.id, folder_id)
    notes = (
        (
            await session.execute(
                select(Note)
                .join(FolderNote, FolderNote.c.note_id == Note.id)
                .where(FolderNote.c.folder_id == folder_id)
                .options(selectinload(Note.author))
                .offset(skip)
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )
    return [note.to_json() for note in notes]


@router.post("/{folder_id}/notes/{note_id}/")
async def add_note_to_folder(
    folder_id: int,
    note_id: int,
    session: AsyncSession = Depends(get_session),
    user: AuthUser = Depends(require_auth),
):
    await ensure_constraints(session, user.id, folder_id)
    link_exists = (
        await session.execute(
            select(
                exists().where(
                    FolderNote.c.folder_id == folder_id,
                    FolderNote.c.note_id == note_id,
                )
            )
        )
    ).scalar_one()
    if link_exists:
        raise AppException(
            status=409,
            payload={c.WORD_MESSAGE: "Note is already in folder"},
        )

    stmt = insert(FolderNote).values(folder_id=folder_id, note_id=note_id)
    await session.execute(stmt)
    await session.commit()
    return Response(status_code=201)
