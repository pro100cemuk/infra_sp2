from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewsViewSet, TitlesViewSet, UserViewSet, signup,
                    get_token)

v1 = DefaultRouter()
v1.register('users', UserViewSet, basename='users')
v1.register('categories', CategoryViewSet, basename='categories')
v1.register('genres', GenreViewSet, basename='genres')
v1.register('titles', TitlesViewSet, basename='titles')

v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)

v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/', include(v1.urls)),
]
