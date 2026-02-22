# shop/management/commands/import_products.py
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File
from backend.shop.models import Category, Product

CSV_FIELDS = ['id','name','category','short_description','price','unit','image_filename','stock_estimate','is_active']

class Command(BaseCommand):
    help = 'Import products from CSV. CSV must have columns: name,category,short_description,price,unit,image_filename,stock_estimate,is_active'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='Path to CSV file')
        parser.add_argument('--images_dir', type=str, default=os.path.join(settings.BASE_DIR, 'media', 'import_images'), help='Directory where images are stored (image filenames must match CSV)')

    def handle(self, *args, **options):
        csvfile = options['csvfile']
        images_dir = options['images_dir']

        if not os.path.exists(csvfile):
            raise CommandError(f"CSV file not found: {csvfile}")

        with open(csvfile, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            created = 0
            updated = 0
            for row in reader:
                name = row.get('name') or row.get('Name')
                if not name:
                    continue
                category_name = row.get('category') or 'Uncategorized'
                cat, _ = Category.objects.get_or_create(name=category_name.strip())
                price = row.get('price') or 0
                unit = row.get('unit') or ''
                desc = row.get('short_description') or ''
                image_filename = row.get('image_filename') or ''
                stock = int(row.get('stock_estimate') or 0)
                is_active = row.get('is_active', 'True').lower() in ('1','true','yes')

                product, created_flag = Product.objects.update_or_create(
                    name=name.strip(),
                    defaults={
                        'category': cat,
                        'description': desc,
                        'price': price,
                        'unit': unit,
                        'stock': stock,
                        'is_active': is_active,
                    }
                )

                # attach image if exists
                if image_filename:
                    image_path = os.path.join(images_dir, image_filename)
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as img_file:
                            product.image.save(image_filename, File(img_file), save=True)
                    else:
                        self.stdout.write(self.style.WARNING(f"Image not found: {image_path} (product {product.name})"))
                product.save()
                if created_flag:
                    created += 1
                else:
                    updated += 1

            self.stdout.write(self.style.SUCCESS(f"Import finished. Created: {created}, Updated: {updated}"))
