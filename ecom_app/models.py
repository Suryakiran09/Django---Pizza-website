from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')

    CATEGORY_CHOICES = [
        ('pizza', 'Pizza'),
        ('burger', 'Burger'),
        ('drink', 'Drink'),
        # Add more choices as needed
    ]

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='pizza',  # Set a default value if needed
    )

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')
    
    def __str__(self):
        return self.user.first_name

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product} - {self.quantity} items in cart {self.cart}"
    

class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Address for {self.user.username}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Initiated', 'Initiated'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Initiated')
    
    def __str__(self):
        return f"Product : {self.product}  Quantity : {self.quantity} Amount : {self.total_amount} Razorpay ID : {self.razorpay_order_id} "