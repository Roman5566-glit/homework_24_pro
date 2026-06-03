from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MessageOut(BaseModel):
    message: str


class TaskIn(BaseModel):
    title: str
    description: Optional[str] = ""
    is_completed: Optional[bool] = False
    deadline: Optional[datetime] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    is_completed: bool
    created_at: datetime
    deadline: Optional[datetime]


class ProductIn(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    stock: int


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int


class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int


class OrderItemOut(BaseModel):
    product_name: Optional[str] = None
    price: float
    quantity: int


class OrderOut(BaseModel):
    id: int
    status: str
    created_at: datetime
    items: list[OrderItemOut]


class GenreIn(BaseModel):
    name: str


class MovieIn(BaseModel):
    title: str
    description: Optional[str] = ""
    release_date: date
    genre_ids: list[int]


class MovieReviewIn(BaseModel):
    text: str
    rating: int


class MovieOut(BaseModel):
    id: int
    title: str
    description: str
    release_date: date
    rating: float
    genres: list[str]


class PostIn(BaseModel):
    title: str
    content: str
    tag_names: list[str] = []


class CommentIn(BaseModel):
    text: str


class CommentOut(BaseModel):
    id: int
    author_username: str
    text: str
    created_at: datetime


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    author_username: str
    created_at: datetime
    tags: list[str]


class ServerIn(BaseModel):
    name: str
    ip_address: str
    is_online: Optional[bool] = True


class ServerMetricIn(BaseModel):
    cpu_usage: float
    ram_usage: float


class ServerOut(BaseModel):
    id: int
    name: str
    ip_address: str
    is_online: bool
    cpu_usage: float
    ram_usage: float


class BookIn(BaseModel):
    title: str
    author: str
    genre: str


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    is_available: bool


class CourseIn(BaseModel):
    title: str
    description: Optional[str] = ""


class CourseOut(BaseModel):
    id: int
    title: str
    description: str


class StudentIn(BaseModel):
    full_name: str
    username: str


class ExamResultIn(BaseModel):
    grade: int


class CourseStatsOut(BaseModel):
    course_title: str
    average_grade: float
    total_students: int
