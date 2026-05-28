from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.title)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.name)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'В процесі'),
        ('shipped', 'Відправлений'),
        ('delivered', 'Доставлений'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return str(self.name)

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    def __str__(self) -> str:
        return str(self.title)

class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField()  

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return str(self.name)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='posts')

    def __str__(self) -> str:
        return str(self.title)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Server(models.Model):
    name = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    is_online = models.BooleanField(default=True)
    cpu_usage = models.FloatField(default=0.0)   # %
    ram_usage = models.FloatField(default=0.0)   # %

    def __str__(self) -> str:
        return f"{self.name} ({self.ip_address})"

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=150)
    genre = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.title)

class BookRental(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='rentals')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return str(self.title)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=255)
    courses = models.ManyToManyField(Course, related_name='students', blank=True)

    def __str__(self) -> str:
        return str(self.full_name)

class ExamResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='exam_results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.IntegerField()  
