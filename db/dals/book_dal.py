
from typing import List, Optional

from sqlalchemy import update,delete,func
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.models.book import Book,Review

class BookDAL():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_book(self,title:str, author: str, genre: str, year_published:int, summary:str):
        new_book = Book(title=title,author=author,genre=genre, year_published=year_published, summary=summary)
        self.db_session.add(new_book)
        await self.db_session.flush()
        return new_book
        
   
                
    async def get_all_books(self) -> list[Book]:
        q = await self.db_session.execute(select(Book).order_by(Book.id))
        return q.scalars().all()

    async def get_book(self, id: int) -> [Book]:
        q = await self.db_session.execute(select(Book).where(Book.id == id))
        return q.scalars().all()

    async def update_book(self, id: int, title: Optional[str], author: Optional[str],genre: Optional[str], year_published: Optional[int],summary: Optional[str]):
        q = update(Book).where(Book.id == id)
        if title:
            q = q.values(title=title)
        if author:
            q = q.values(author=author)
        if genre:
            q = q.values(genre=genre)   
        if year_published:
            q = q.values(year_published=year_published)
        if summary:
            q = q.values(summary=summary)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)

    async def delete_book(self, id: int):
        result = await self.db_session.execute(select(Book).where(Book.id==id))
        book = result.scalar_one_or_none()
        if book:
            # Delete the book
            await self.db_session.execute(delete(Book).where(Book.id == id))
            await self.db_session.commit()
            return True
        return False

    async def add_review(self, book_id: int, user_id:int, review_text: str, rating: int):
        result = await self.db_session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        new_review = Review(book_id=book_id,user_id=user_id,review_text=review_text, rating=rating)
        self.db_session.add(new_review)
        await self.db_session.flush()
        return new_review


    async def get_all_reviews(self) -> list[Review]:
        q = await self.db_session.execute(select(Review).order_by(Review.id))
        return q.scalars().all()

    async def get_book_summary_and_rating(self, book_id: int):
        # Fetch the book summary and aggregate rating for a specific book
        book_query = await self.db_session.execute(
            select(Book.title, Book.summary)
            .where(Book.id == book_id)
        )
        book = book_query.fetchone()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        # Calculate the average rating for the book
        rating_query = await self.db_session.execute(
            select(func.avg(Review.rating))
            .where(Review.book_id == book_id)
        )
        avg_rating = rating_query.scalar()

        return {
            "title": book.title,
            "summary": book.summary,
            "average_rating": avg_rating if avg_rating else 0.0
        }

    async def get_user_highly_rated_books(self, user_id: int, rating_threshold: int = 4):
        # Query to get books the user has rated above a certain threshold
        result = await self.db_session.execute(
            select(Book)
            .join(Review)
            .where(Review.user_id == user_id, Review.rating >= rating_threshold)
        )
        return result.scalars().all()

    async def get_similar_books(self, book: Book, user_id: int):
        # Find books by the same author or in the same genre that the user has not rated
        similar_books = await self.db_session.execute(
            select(Book)
            .outerjoin(Review)
            .where(
                (Book.author == book.author) | (Book.genre == book.genre),
                Book.id != book.id,  # Exclude the original book
                Review.user_id != user_id  # Exclude books the user has already rated
            )
        )
        return similar_books.scalars().all()

    async def get_user_based_recommendations(self, user_id: int):
        # Get highly rated books by the user
        highly_rated_books = await self.get_user_highly_rated_books(user_id)
        
        recommendations = []
        for book in highly_rated_books:
            similar_books = await self.get_similar_books(book, user_id)
            recommendations.extend(similar_books)
        
        # Deduplicate recommendations
        unique_recommendations = {book.id: book for book in recommendations}.values()
        return list(unique_recommendations)



       
        
        
                