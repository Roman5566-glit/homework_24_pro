from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from core.api import (
    task_router, ecommerce_router, movie_router,
    blog_router, server_router, library_router, student_router
)


api = NinjaAPI(
    title="REST API Блок на Django Ninja (ДЗ 24)",
    version="1.0.0",
    description="Комплексна реалізація 7 індивідуальних API підсистем з автентифікацією"
)

api.add_router('/taskmanager/', task_router, tags=["1. Task Manager"])
api.add_router('/ecommerce/', ecommerce_router, tags=["2. E-commerce"])
api.add_router('/movies/', movie_router, tags=["3. Movie Collection"])
api.add_router('/blog/', blog_router, tags=["4. Blog Platform"])
api.add_router('/monitoring/', server_router, tags=["5. Server Monitoring"])
api.add_router('/library/', library_router, tags=["6. Book Library"])
api.add_router('/education/', student_router, tags=["7. Student & Course Management"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),     
]
