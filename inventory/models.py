#models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=1)

    def is_below_minimum(self):
        return self.stock < self.min_stock

    def __str__(self):
        return self.name

class StockMovement(models.Model):
    IN = 'IN'
    OUT = 'OUT'
    MOVEMENT_CHOICES = [
        (IN, 'Entrada'),
        (OUT, 'Salida'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_CHOICES)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def clean(self):
        if self.movement_type == self.OUT and self.product.stock < self.quantity:
            raise ValidationError(f"No hay suficiente stock para realizar esta salida: {self.product.stock} disponibles.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Validamos antes de guardar
        if self.pk is None:
            if self.movement_type == self.IN:
                self.product.stock += self.quantity
            elif self.movement_type == self.OUT:
                self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} ({self.quantity})"
