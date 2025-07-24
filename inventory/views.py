# views.py content
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Product, StockMovement, Supplier, Category
from .forms import StockMovementForm, ProductForm , CategoryForm, SupplierForm
from django.db.models import Q, Sum, F
import csv
from django.http import HttpResponse
from django.utils.timezone import now
from datetime import timedelta
from django.contrib import messages  # Añadir import
import io

def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/agregar_categoria.html', {'form': form})


def agregar_proveedor(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/agregar_proveedor.html', {'form': form})
    
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # o donde quieras redirigir
    else:
        form = ProductForm()
    return render(request, 'inventory/agregar_producto.html', {'form': form})
    
def dashboard(request):
    low_stock_products = Product.objects.filter(stock__lt=F('min_stock'))
    return render(request, 'inventory/dashboard.html', {
        'low_stock_products': low_stock_products
    })


def new_movement(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StockMovementForm()
    return render(request, 'inventory/new_movement.html', {'form': form})


def product_list(request):
    products = Product.objects.all()
    supplier = request.GET.get('supplier')
    category = request.GET.get('category')

    if supplier:
        products = products.filter(supplier__id=supplier)
    if category:
        products = products.filter(category__id=category)

    suppliers = Supplier.objects.all()
    categories = Category.objects.all()

    return render(request, 'inventory/product_list.html', {
        'products': products,
        'suppliers': suppliers,
        'categories': categories
    })

def import_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        try:
            for row in reader:
                # Limpiar claves y valores (evitar errores con None)
                row = { (key or '').strip(): (value or '').strip() for key, value in row.items() }

                # Validación mínima
                if not all(k in row for k in ['name', 'stock', 'min_stock', 'category', 'supplier']):
                    messages.warning(request, "Faltan columnas obligatorias en el archivo CSV.")
                    return redirect('import_csv')

                name = row['name']
                if not name:
                    continue  # Omitir filas sin nombre

                # Parsear stock y min_stock
                stock = int(row['stock']) if row['stock'].isdigit() else 0
                min_stock_str = row.get('min_stock', '')
                min_stock = int(min_stock_str) if min_stock_str.isdigit() else None

                category_name = row.get('category', '')
                supplier_name = row.get('supplier', '')

                if not category_name or not supplier_name:
                    messages.warning(request, f"Fila con datos incompletos omitida: {row}")
                    continue

                # Crear o recuperar objetos relacionados
                category, _ = Category.objects.get_or_create(name=category_name)
                supplier, _ = Supplier.objects.get_or_create(name=supplier_name)

                # Verificar si el producto ya existe
                product = Product.objects.filter(
                    name=name,
                    category=category,
                    supplier=supplier
                ).first()

                if product:
                    product.stock += stock
                    if min_stock is not None and min_stock > 0:
                        product.min_stock = min_stock
                    product.save()
                else:
                    Product.objects.create(
                        name=name,
                        stock=stock,
                        min_stock=min_stock if min_stock is not None else 0,
                        category=category,
                        supplier=supplier,
                    )

            messages.success(request, "Productos importados correctamente.")
            return redirect('product_list')

        except UnicodeDecodeError:
            messages.error(request, "Error de codificación. Asegúrate de que el archivo está en formato UTF-8 o Latin1.")
        except KeyError as e:
            messages.error(request, f"Falta la columna: {e}")
        except Exception as e:
            messages.error(request, f"Error al importar: {str(e)}")

    return render(request, 'inventory/import_csv.html')


def movements_chart(request):
    recent_days = 7
    end_date = now().date()
    start_date = end_date - timedelta(days=recent_days - 1)

    movements = (
        StockMovement.objects
        .filter(date__date__range=(start_date, end_date))
        .values('date__date', 'movement_type')
        .annotate(total=Sum('quantity'))
        .order_by('date__date')
    )

    dates = [str(start_date + timedelta(days=i)) for i in range(recent_days)]
    in_data = [0] * recent_days
    out_data = [0] * recent_days

    for m in movements:
        idx = dates.index(str(m['date__date']))
        if m['movement_type'] == 'IN':
            in_data[idx] = m['total']
        else:
            out_data[idx] = m['total']

    return render(request, 'inventory/movements_chart.html', {
        'dates': dates,
        'in_data': in_data,
        'out_data': out_data,
    })


class StockMovementListView(ListView):
    model = StockMovement
    template_name = 'inventory/stockmovement_list.html'
    context_object_name = 'movements'
    ordering = ['-date']
    paginate_by = 20


class StockMovementCreateView(CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/stockmovement_form.html'
    success_url = reverse_lazy('stockmovement_list')
