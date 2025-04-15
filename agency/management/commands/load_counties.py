from django.core.management.base import BaseCommand
from agency.models import County

class Command(BaseCommand):
    help = "Load Oregon counties into the database"

    def handle(self, *args, **options):
        counties = [
            "Baker", "Benton", "Clackamas", "Clatsop", "Columbia", "Coos", "Crook",
            "Curry", "Deschutes", "Douglas", "Gilliam", "Grant", "Harney", "Hood River",
            "Jackson", "Jefferson", "Josephine", "Klamath", "Lake", "Lane", "Lincoln",
            "Linn", "Malheur", "Marion", "Morrow", "Multnomah", "Polk", "Sherman",
            "Tillamook", "Umatilla", "Union", "Wallowa", "Wasco", "Washington", "Wheeler", "Yamhill"
        ]

        created = 0
        for name in counties:
            _, was_created = County.objects.get_or_create(name=name)
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} counties added."))
