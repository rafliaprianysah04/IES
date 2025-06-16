from django.core.management.base import BaseCommand
from surveyor.models import MappingContainer
from itertools import product

class Command(BaseCommand):
    help = "Inisialisasi semua kemungkinan kombinasi mapping container"

    def handle(self, *args, **kwargs):
        blocks = ['A', 'B', 'C', 'D', 'E', 'F', 'W', 'X', 'Z']
        specs = [f'{i:02}' for i in range(1, 16)]
        rows = [f'{i:02}' for i in range(1, 16)]
        tiers = [str(i) for i in range(1, 8)]

        total = 0
        for block, spec, row, tier in product(blocks, specs, rows, tiers):
            obj, created = MappingContainer.objects.get_or_create(
                block=block,
                spec=spec,
                row=row,
                tier=tier,
                defaults={'container_no': None}
            )
            if created:
                total += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Berhasil mengisi {total} data mapping container."))
