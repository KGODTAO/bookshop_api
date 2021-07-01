from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Book, Review, OrderItems, Order

User = get_user_model()


class BooksListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'price', 'image')


class ReviewAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.first_name and not instance.last_name:
            representation['full name'] = 'Анонимный пользователь'
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ('id', 'author')

    def validate_book(self, book):
        request = self.context.get('request')
        if book.reviews.filter(author=request.user).exists():
            raise serializers.ValidationError('Вы не можете добавить второй товар')
        return book

    def validate_rating(self, rating):
        if not rating in range(1, 6):
            raise serializers.ValidationError('Рейтинг должен быть от 1 до 5')
        return rating

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['author'] = ReviewAuthorSerializer(instance.author).data
        return rep


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ('book', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    books = OrderItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = ('books', 'notes')

    def create(self, validated_data):
        total_sum = 0
        request = self.context.get('request')
        validated_data['user'] = request.user
        validated_data['status'] = 'new'
        validated_data['total_sum'] = total_sum
        books = validated_data.pop('books')
        order = Order.objects.create(**validated_data)
        for prod in books:
            total_sum += prod['book'].price * prod['quantity']
            OrderItems.objects.create(order=order, **prod)
        order.total_sum = total_sum
        order.save()
        return order


class BooksDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def get_rating(self, instance):
        total_rating = sum(instance.reviews.values_list('rating', flat=True))
        reviews_count = instance.reviews.count()
        rating = total_rating / reviews_count if reviews_count > 0 else 0
        return round(rating, 1)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        representation['rating'] = self.get_rating(instance)
        representation['likes'] = self.get_like(instance)
        return representation


    def get_like(self, instance):
        likes_count = instance.reviews.count()
        return likes_count
