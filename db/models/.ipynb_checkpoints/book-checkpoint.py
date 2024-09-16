from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from db.config import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    year_published = Column(Integer, nullable=False)
    summary = Column(String, nullable=False)
    # Relationship to Review
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer,ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, nullable=False)
    review_text = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    # Relationship to Book
    book = relationship("Book", back_populates="reviews")


  