from django.urls import path
from .views import register_user, user_login, user_logout, create_post, get_post_detail, thread_list, favorites_list, add_to_favorites, remove_from_favorites, delete_post

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('new/', create_post, name='new_post'),
    path('posts/<uuid:post_id>/', get_post_detail, name='post_detail'),
    path('posts/delete/<uuid:post_id>/', delete_post, name='delete_post'),
    path('threads/', thread_list, name='thread_list'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('favorites/add/<uuid:post_id>/', add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<uuid:post_id>/', remove_from_favorites, name='remove_from_favorites'),
]
