import logging
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from .models import (
    Task,
    Product,
    CartItem,
    Order,
    OrderItem,
    Genre,
    Movie,
    MovieReview,
    Tag,
    Post,
    Comment,
    Server,
    Book,
    BookRental,
    Course,
    StudentProfile,
    ExamResult,
)
from .schemas import (
    MessageOut,
    TaskIn,
    TaskOut,
    ProductIn,
    ProductOut,
    CartItemOut,
    OrderOut,
    GenreIn,
    MovieIn,
    MovieReviewIn,
    MovieOut,
    PostIn,
    CommentIn,
    PostOut,
    ServerIn,
    ServerMetricIn,
    ServerOut,
    BookIn,
    BookOut,
    CourseIn,
    CourseOut,
    StudentIn,
    ExamResultIn,
    CourseStatsOut,
)


task_router = Router(auth=django_auth)


@task_router.get(...)
@task_router.get("/tasks", response=list[TaskOut])
def get_tasks(
    request, status: Optional[bool] = None, order_by: Optional[str] = "created_at"
):
    """Отримання завдань користувача з фільтрацією та сортуванням"""
    queryset = Task.objects.filter(user=request.auth)
    if status is not None:
        queryset = queryset.filter(is_completed=status)
    if order_by in ["created_at", "-created_at", "deadline", "-deadline"]:
        queryset = queryset.order_by(order_by)
    return queryset


@task_router.post("/tasks", response=TaskOut)
def create_task(request, payload: TaskIn):
    return Task.objects.create(user=request.auth, **payload.dict())


@task_router.put("/tasks/{task_id}", response=TaskOut)
def update_task(request, task_id: int, payload: TaskIn):
    task = get_object_or_404(Task, id=task_id, user=request.auth)
    for attr, value in payload.dict().items():
        setattr(task, attr, value)
    task.save()
    return task


@task_router.delete("/tasks/{task_id}", response=MessageOut)
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id, user=request.auth)
    task.delete()
    return {"message": "Завдання успішно видалено."}


ecommerce_router = Router(auth=django_auth)


@ecommerce_router.get("/products", response=list[ProductOut])
def list_products(request):
    return Product.objects.all()


@ecommerce_router.post("/products", response=ProductOut)
def create_product(request, payload: ProductIn):
    return Product.objects.create(**payload.dict())


@ecommerce_router.post("/cart/add/{product_id}", response=MessageOut)
def add_to_cart(request, product_id: int, qty: int = 1):
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(user=request.auth, product=product)
    if not created:
        item.quantity += qty
    else:
        item.quantity = qty
    item.save()
    return {"message": f"Товар '{product.name}' додано до кошика."}


@ecommerce_router.post("/cart/remove/{product_id}", response=MessageOut)
def remove_from_cart(request, product_id: int):
    item = get_object_or_404(CartItem, user=request.auth, product_id=product_id)
    item.delete()
    return {"message": "Товар видалено з кошика."}


@ecommerce_router.post("/checkout", response=OrderOut)
def checkout_order(request):
    """Оформлення замовлення з товарів у кошику"""
    cart_items = CartItem.objects.filter(user=request.auth)
    if not cart_items.exists():
        raise Exception("Кошик порожній.")

    order = Order.objects.create(user=request.auth, status="processing")
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity,
        )
    cart_items.delete()

    return {
        "id": order.id,
        "status": order.status,
        "created_at": order.created_at,
        "items": [
            {
                "product_name": i.product.name if i.product else "Видалений товар",
                "price": float(i.price),
                "quantity": i.quantity,
            }
            for i in order.items.all()
        ],
    }


movie_router = Router(auth=django_auth)


@movie_router.get("/", response=list[MovieOut])
def get_movies(
    request,
    genre: Optional[str] = None,
    rating: Optional[float] = None,
    search: Optional[str] = None,
):
    queryset = Movie.objects.all()
    if search:
        queryset = queryset.filter(title__icontains=search)
    if genre:
        queryset = queryset.filter(genres__name__iexact=genre)
    if rating:
        queryset = queryset.filter(rating__gte=rating)

    return [
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "release_date": m.release_date,
            "rating": float(m.rating),
            "genres": [g.name for g in m.genres.all()],
        }
        for m in queryset
    ]


@movie_router.post("/", response=MessageOut)
def create_movie(request, payload: MovieIn):
    movie = Movie.objects.create(
        title=payload.title,
        description=payload.description,
        release_date=payload.release_date,
    )
    movie.genres.set(payload.genre_ids)
    return {"message": f"Фільм '{movie.title}' додано до бази."}


@movie_router.post("/{movie_id}/review", response=MessageOut)
def add_movie_review(request, movie_id: int, payload: MovieReviewIn):
    movie = get_object_or_404(Movie, id=movie_id)
    MovieReview.objects.create(
        movie=movie, user=request.auth, text=payload.text, rating=payload.rating
    )

    avg = movie.reviews.aggregate(Avg("rating"))["rating__avg"]
    movie.rating = avg or 0.0
    movie.save()
    return {"message": "Відгук успішно збережено."}


blog_router = Router(auth=django_auth)


@blog_router.get("/posts", response=list[PostOut])
def list_posts(request):
    return [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "author_username": p.author.username,
            "created_at": p.created_at,
            "tags": [t.name for t in p.tags.all()],
        }
        for p in Post.objects.all()
    ]


@blog_router.post("/posts", response=MessageOut)
def create_post(request, payload: PostIn):
    post = Post.objects.create(
        author=request.auth, title=payload.title, content=payload.content
    )
    for tag_name in payload.tag_names:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        post.tags.add(tag)
    return {"message": "Пост успішно опубліковано."}


@blog_router.post("/posts/{post_id}/comment", response=MessageOut)
def add_comment(request, post_id: int, payload: CommentIn):
    post = get_object_or_404(Post, id=post_id)
    Comment.objects.create(post=post, author=request.auth, text=payload.text)
    return {"message": "Коментар додано."}


server_router = Router(auth=django_auth)


@server_router.get("/servers", response=list[ServerOut])
def list_servers(request):
    return Server.objects.all()


@server_router.post("/servers", response=ServerOut)
def add_server(request, payload: ServerIn):
    return Server.objects.create(**payload.dict())


@server_router.post("/servers/{server_id}/metrics", response=ServerOut)
def update_server_metrics(request, server_id: int, payload: ServerMetricIn):
    """Оновлення метрик. Якщо значення критичні, спрацьовує тригер сповіщення"""
    server = get_object_or_404(Server, id=server_id)
    server.cpu_usage = payload.cpu_usage
    server.ram_usage = payload.ram_usage
    server.save()

    if server.cpu_usage > 90.0 or server.ram_usage > 90.0:
        logger.warning(
            f"[CRITICAL ALERT] Сервер {server.name} ({server.ip_address}) перевищив ліміти! CPU: {server.cpu_usage}%, RAM: {server.ram_usage}%"
        )
        print(f"[ALERT] {server.name} У КРИТИЧНОМУ СТАНІ!")

    return server


library_router = Router(auth=django_auth)


@library_router.get("/books", response=list[BookOut])
def search_books(request, search_query: Optional[str] = None):
    queryset = Book.objects.all()
    if search_query:
        queryset = (
            queryset.filter(title__icontains=search_query)
            | queryset.filter(author__icontains=search_query)
            | queryset.filter(genre__icontains=search_query)
        )
    return queryset


@library_router.post("/books", response=BookOut)
def add_book(request, payload: BookIn):
    return Book.objects.create(**payload.dict())


@library_router.post("/books/{book_id}/rent", response=MessageOut)
def rent_book(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    if not book.is_available:
        return 400, {"message": "Книга вже орендована іншим читачем."}

    BookRental.objects.create(book=book, user=request.auth)
    book.is_available = False
    book.save()
    return {"message": f"Ви успішно орендували книгу '{book.title}'."}


student_router = Router(auth=django_auth)


@student_router.post("/courses", response=CourseOut)
def create_course(request, payload: CourseIn):
    return Course.objects.create(**payload.dict())


@student_router.post("/enroll/{course_id}", response=MessageOut)
def enroll_student(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    profile, _ = StudentProfile.objects.get_or_create(
        user=request.auth, defaults={"full_name": request.auth.username}
    )
    profile.courses.add(course)
    return {"message": f"Студент записаний на курс '{course.title}'."}


@student_router.post("/courses/{course_id}/grade/{student_id}", response=MessageOut)
def grade_student(request, course_id: int, student_id: int, payload: ExamResultIn):
    student = get_object_or_404(StudentProfile, id=student_id)
    course = get_object_or_404(Course, id=course_id)
    ExamResult.objects.create(student=student, course=course, grade=payload.grade)
    return {"message": "Оцінка успішно виставлена."}


@student_router.get("/courses/{course_id}/stats", response=CourseStatsOut)
def get_course_stats(request, course_id: int):
    """Підрахунок середньої оцінки за кожним курсом через ORM агрегацію"""
    course = get_object_or_404(Course, id=course_id)
    stats = ExamResult.objects.filter(course=course).aggregate(
        avg_grade=Avg("grade"), total=Count("id")
    )

    return {
        "course_title": course.title,
        "average_grade": round(stats["avg_grade"] or 0.0, 2),
        "total_students": stats["total"] or 0,
    }
