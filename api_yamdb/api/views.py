from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, Func
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import ADMIN_EMAIL
from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .permissions import (IsAuthorAdminModeratorOrReadOnly, IsRoleAdmin,
                          ReadOnly)
from .serializers import (AdminUserSerializer, CategorySerializer,
                          CommentsSerializer, GenreSerializer,
                          ReviewsSerializer, SignupSerializer,
                          TitlesCreateSerializer, TitlesSerializer,
                          TokenSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsRoleAdmin]
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    lookup_value_regex = r'[\w\@\.\+\-]+'
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=[IsAuthenticated]
    )
    def about_me(self, request):
        serializer = UserSerializer(request.user)
        if not request.method == 'PATCH':
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    try:
        user, created = User.objects.get_or_create(
            username=username,
            email=email)
    except Exception:
        raise serializers.ValidationError
    send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.validated_data.get('confirmation_code')
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    token = AccessToken.for_user(user)
    return Response(
        {'token': str(token)}, status=status.HTTP_200_OK
    )


def send_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    subject = 'Код подтверждения на ресурсе yamdb'
    message = f'{confirmation_code} - ваш код авторизации'
    admin_email = ADMIN_EMAIL
    user_email = [user.email]
    return send_mail(subject, message, admin_email, user_email)


class ListCreateDestroy(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsRoleAdmin | ReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    @action(
        detail=False, methods=['delete'],
        url_path=r'(?P<slug>\w+)',
        lookup_field='slug'
    )
    def get_genre_or_category(self, request, slug):
        object = self.get_object()
        if isinstance(object, Genre):
            serializer = GenreSerializer(object)
        else:
            serializer = CategorySerializer(object)
        object.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ListCreateDestroy):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroy):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class Round0(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 0)'


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Round0(Avg('reviews__score')))
    serializer_class = TitlesSerializer
    permission_classes = [IsRoleAdmin | ReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitlesCreateSerializer
        return TitlesSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=int(self.kwargs.get('title_id')))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=int(self.kwargs.get('title_id')))
        return title.reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=int(self.kwargs.get('review_id')),
            title__id=int(self.kwargs.get('title_id'))
        )
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=int(self.kwargs.get('review_id')),
            title__id=int(self.kwargs.get('title_id'))
        )
        return review.comments.all()
