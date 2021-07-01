from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, primary_key=True)

    def __str__(self):
        return self.title


class Book(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    image = models.ImageField(upload_to='books', blank=True, null=True)

    class Meta:
        ordering = ['title', 'price']

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['author', 'book']


class StatusChoices(models.TextChoices):
    new = ('new', 'Новый'),
    in_progress = ('in_progress', 'В обработке')
    done = ('done', 'Выполнен')
    canceled = ('canceled', 'Отменен')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='orders')
    book = models.ManyToManyField(Book, through='OrderItems')
    status = models.CharField(max_length=20, choices=StatusChoices.choices)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING, related_name='order_items')
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ['order', 'book']


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)

