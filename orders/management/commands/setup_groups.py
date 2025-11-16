from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from orders.models import Order, Product, ScanLog, ImageAttachment

class Command(BaseCommand):
    help = 'Create user groups and set permissions for role-based access control'

    def handle(self, *args, **options):
        # Define groups and their permissions
        groups_permissions = {
            'administrators': [
                'add_order', 'change_order', 'delete_order', 'view_order',
                'add_product', 'change_product', 'delete_product', 'view_product',
                'add_scanlog', 'view_scanlog',
                'add_imageattachment', 'change_imageattachment', 'delete_imageattachment', 'view_imageattachment',
            ],
            'managers': [
                'add_order', 'change_order', 'view_order',
                'add_product', 'change_product', 'view_product',
                'view_scanlog',
                'add_imageattachment', 'view_imageattachment',
            ],
            'operators': [
                'add_order', 'view_order',
                'view_product',
                'view_scanlog',
                'add_imageattachment', 'view_imageattachment',
            ],
            'warehouse_staff': [
                'view_order',
                'view_product',
                'view_scanlog',
                'view_imageattachment',
            ],
        }

        # Get content types
        order_content_type = ContentType.objects.get_for_model(Order)
        product_content_type = ContentType.objects.get_for_model(Product)
        scanlog_content_type = ContentType.objects.get_for_model(ScanLog)
        imageattachment_content_type = ContentType.objects.get_for_model(ImageAttachment)

        # Create groups and assign permissions
        for group_name, permission_codenames in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Add new permissions
            for codename in permission_codenames:
                try:
                    # Try to find the permission
                    permission = Permission.objects.get(codename=codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(f'Warning: Permission {codename} does not exist')
            
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{status} group: {group_name} with {group.permissions.count()} permissions'))

        self.stdout.write(self.style.SUCCESS('Successfully set up all user groups and permissions!'))
        self.stdout.write('\nGroups created:')
        self.stdout.write('  - administrators: Full access to all features')
        self.stdout.write('  - managers: Can create/update orders and products')
        self.stdout.write('  - operators: Can create orders and upload images')
        self.stdout.write('  - warehouse_staff: Can only view orders and products')
