from sqlalchemy import Column, ForeignKey, Integer, Table

import noter.utils.constants as c
from noter.models.db.meta import BaseModel

FolderNote = Table(
    c.TBL_FOLDER_NOTES,
    BaseModel.metadata,
    Column(
        "folder_id",
        Integer,
        ForeignKey(f"{c.TBL_FOLDERS}.{c.WORD_ID}"),
        primary_key=True,
    ),
    Column(
        "note_id",
        Integer,
        ForeignKey(f"{c.TBL_NOTES}.{c.WORD_ID}"),
        primary_key=True,
    ),
)
