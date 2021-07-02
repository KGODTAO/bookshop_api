from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .filters import BookFilter, OrderFilter
from .models import Book, Review, Order, WishList, FavouriteList
from .permissions import IsAuthorOrAdminPermission, DenyAll
from .serializers import BooksListSerializer, BooksDetailsSerializer, ReviewSerializer, OrderSerializer, \
    FavouriteSerializer


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = BookFilter
    ordering_fields = ['title', 'price']

    def get_serializer_class(self):
        if self.action == 'list':
            return BooksListSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action in ['create_review', 'like']:
            return [IsAuthenticated()]
        return []

    # api/v1/products/id/create_review
    @action(detail=True, methods=['POST'])
    def create_review(self, request, pk):
        # product = self.get_object()
        data = request.data.copy()
        data['books'] = pk
        serializer = ReviewSerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)

    #/api/v1/products/id/like
    @action(detail=True, methods=['POST'])
    def like(self, request, pk):
        book = self.get_object()
        user = request.user
        like_obj, created = WishList.objects.get_or_create(book=book, user=user)
        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save()
            return Response('disliked')
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response('liked')

    @action(detail=True, methods=['POST'])
    def favourite(self, request, pk):
        title = self.get_object()
        user = request.user
        favourite_obj, created = FavouriteList.objects.get_or_create(title=title, user=user)
        if favourite_obj.is_favourite:
            favourite_obj.is_favourite = False
            favourite_obj.delete()
            return Response('remove from favourites')
        else:
            favourite_obj.is_favourite = True
            favourite_obj.save()
            return Response('add to favourites')

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                  Q(description__icontains=q))
        serializer = BooksListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)





class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthorOrAdminPermission()]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = OrderFilter
    ordering_fields = ['total_sum', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAdminUser()]
        else:
            return [DenyAll()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class FavouriteViewSet(viewsets.ModelViewSet):
    queryset = FavouriteList.objects.all()
    serializer_class = FavouriteSerializer
    permission_classes = [IsAuthenticated, ]