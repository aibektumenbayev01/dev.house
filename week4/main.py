from itertools import count
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, HttpUrl
class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)

class BookmarkRead(BookmarkCreate):
    id: int

app = FastAPI(title="Bookmarks API")
bookmarks: dict[int, BookmarkRead] = {}
bookmark_ids = count(1)

@app.get("/bookmarks", response_model=list[BookmarkRead])
async def list_bookmarks():
    return list(bookmarks.values())

@app.get("/bookmarks/{id}", response_model=BookmarkRead)
async def get_bookmark(id: int):
    bookmark = bookmarks.get(id)
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark

@app.post("/bookmarks", response_model=BookmarkRead, status_code=201)
async def create_bookmark(data: BookmarkCreate):
    bookmark = BookmarkRead(id=next(bookmark_ids), **data.model_dump())
    bookmarks[bookmark.id] = bookmark
    return bookmark

@app.put("/bookmarks/{id}", response_model=BookmarkRead)
async def replace_bookmark(id: int, data: BookmarkCreate):
    if id not in bookmarks:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    bookmark = BookmarkRead(id=id, **data.model_dump())
    bookmarks[id] = bookmark
    return bookmark

@app.delete("/bookmarks/{id}", response_model=None, status_code=204)
async def delete_bookmark(id: int):
    if bookmarks.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return Response(status_code=204)
