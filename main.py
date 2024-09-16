import uvicorn
from fastapi import FastAPI, HTTPException
from typing import List, Optional

from db.config import engine, Base, async_session
from db.dals.book_dal import BookDAL
from db.models.book import Book, Review
from langchain_community.llms import Ollama
# Initialize the Ollama LLM (this can be done during startup)
llm = Ollama(model="llama3")
 
app = FastAPI(
    title="My API",
    description="This is a sample FastAPI application.",
    version="1.0.0",
    docs_url="/docs",    # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json"  # OpenAPI schema
)

# Define the root route ("/") that will return a JSON response
@app.get("/")
async def hello_world():
    return {"message": "Hello, World!"}

    
@app.on_event("startup")
async def startup():
    # Create db tables
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully.")
        except Exception as e:
            print(f"An error occurred while creating tables: {e}")

@app.post("/books")
async def create_book(title: str, author: str, genre: str, year_published: int, summary:str):
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            #return await book_dal.create_book(title, author, genre, year_published, summary)
            new_book = await book_dal.create_book(title, author, genre, year_published, summary)
            print(f"Book created: {new_book}")  # Debug: Print the created book details
            return new_book
            

    
@app.get("/books")
async def get_all_books() -> list[dict]:
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            #return await book_dal.get_all_books()
            books = await book_dal.get_all_books()
            # Manually serialize SQLAlchemy models to dictionaries
            return [{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre, 
                     "year_published": book.year_published, "summary": book.summary} for book in books]

@app.get("/books/{id}")
async def get_book(id: int):
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            book = await book_dal.get_book(id)
            return book
            
@app.put("/books/{id}")
async def update_book(id: int, title: Optional[str] = None, author: Optional[str] = None, genre: Optional[str] = None, year_published: Optional[int] = None, summary: Optional[str] = None):
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            return await book_dal.update_book(id, title, author, genre, year_published, summary)

@app.delete("/books/{id}")
async def delete_book(id: int):
    async with async_session() as session:
        
        book_dal = BookDAL(session)
        success = await book_dal.delete_book(id)
        if success:
            return {"message": "Book deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books/{id}/reviews")
async def add_review(book_id: int, user_id:int, review_text: str, rating: int):
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            new_review = await book_dal.add_review(book_id,user_id,review_text,rating)
            return {"message": "Review added successfully", "review": new_review}

@app.get("/reviews")
async def get_all_reviews() -> list[dict]:
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            #return await book_dal.get_all_reviews()
            reviews = await book_dal.get_all_reviews()
            # Manually serialize SQLAlchemy models to dictionaries
            return [{"id": review.id, "book_id": review.book_id, "user_id": review.user_id, "review_text": review.review_text, 
                     "rating": review.rating} for review in reviews]

@app.get("/books/{book_id}/summary-rating")
async def get_book_summary_and_rating(book_id: int):
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            result = await book_dal.get_book_summary_and_rating(book_id)
            return result

@app.get("/users/{user_id}/recommendations")
async def get_user_based_recommendations(user_id: int):
    async with async_session() as session:
        async with session.begin():
            book_dal = BookDAL(session)
            recommended_books = await book_dal.get_user_based_recommendations(user_id)
            # Serialize the recommendations
            return [
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "genre": book.genre
                }
                for book in recommended_books
            ]
            
# Endpoint for generating text (e.g., joke, summary, etc.)
@app.post("/generate_summary/")
async def generate_summary(book_content: str, summary_length:int):
    """
    Generate text based on a given prompt using the Llama3 model via Ollama.
    """
    try:
        prompt = (
            f"Generate a concise summary for the following text. "
            f"Please limit the summary to {summary_length} characters. "
            f"Content: {book_content}"
        )
        # Invoke the Ollama LLM to get the response
        result = llm.invoke(prompt)

        # Return the generated text as a response
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {e}")

if __name__ == '__main__':
    uvicorn.run("main:app", port=1111, host='127.0.0.1', reload=True)