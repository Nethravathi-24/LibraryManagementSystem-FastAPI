from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# DATA
# -----------------------------
books = [
    {"id": 1, "title": "Python Basics", "author": "John", "category": "Programming"},
    {"id": 2, "title": "Data Science", "author": "Smith", "category": "Programming"},
    {"id": 3, "title": "History of India", "author": "Raj", "category": "History"},
    {"id": 4, "title": "Maths 101", "author": "Kumar", "category": "Education"},
]

borrowed_books = []

# -----------------------------
# MODELS
# -----------------------------
class Book(BaseModel):
    title: str
    author: str
    category: str

class Borrow(BaseModel):
    user: str
    book_id: int

# -----------------------------
# BASIC APIs
# -----------------------------
@app.get("/")
def home():
    return {"message": "Library API running"}

@app.get("/books")
def get_books():
    return {"books": books}

@app.get("/books/count")
def count_books():
    return {"total_books": len(books)}

# -----------------------------
# SEARCH
# -----------------------------
@app.get("/books/search")
def search_books(keyword: str):
    result = [b for b in books if keyword.lower() in b["title"].lower()]
    if not result:
        return {"message": f"No books found for {keyword}"}
    return {"total_found": len(result), "books": result}

# -----------------------------
# SORT
# -----------------------------
@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    if sort_by not in ["title", "author"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by")

    sorted_books = sorted(
        books,
        key=lambda x: x[sort_by],
        reverse=(order == "desc")
    )

    return {"sorted": sorted_books}

# -----------------------------
# PAGINATION
# -----------------------------
@app.get("/books/page")
def paginate(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    total_pages = (len(books) + limit - 1) // limit

    return {
        "page": page,
        "total_pages": total_pages,
        "books": books[start:end]
    }

# -----------------------------
# COMBINED (SEARCH + SORT + PAGE)
# -----------------------------
@app.get("/books/browse")
def browse(
    keyword: str = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = 1,
    limit: int = 2
):
    result = books

    # Search
    if keyword:
        result = [b for b in result if keyword.lower() in b["title"].lower()]

    # Sort
    if sort_by not in ["title", "author"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by")

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    # Pagination
    start = (page - 1) * limit
    end = start + limit

    return {
        "total_found": len(result),
        "page": page,
        "books": result[start:end]
    }

# -----------------------------
# CRUD
# -----------------------------
@app.post("/books")
def add_book(book: Book):
    new_book = book.dict()
    new_book["id"] = len(books) + 1
    books.append(new_book)
    return {"message": "Book added", "book": new_book}

@app.put("/books/{book_id}")
def update_book(book_id: int, updated: Book):
    for b in books:
        if b["id"] == book_id:
            b.update(updated.dict())
            return {"message": "Updated", "book": b}
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for b in books:
        if b["id"] == book_id:
            books.remove(b)
            return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Book not found")

# -----------------------------
# WORKFLOW (BORROW)
# -----------------------------
@app.post("/borrow")
def borrow_book(data: Borrow):
    for b in books:
        if b["id"] == data.book_id:
            borrowed_books.append({
                "user": data.user,
                "book_id": data.book_id
            })
            return {"message": "Book borrowed"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/borrowed")
def get_borrowed():
    return {"borrowed_books": borrowed_books}

# -----------------------------
# ⚠️ ALWAYS KEEP THIS LAST
# -----------------------------
@app.get("/books/{book_id}")
def get_book(book_id: int):
    for b in books:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="Book not found")