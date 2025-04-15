from agency.models import County

OREGON_COUNTIES = [
    "Baker", "Benton", "Clackamas", "Clatsop", "Columbia", "Coos", "Crook", "Curry",
    "Deschutes", "Douglas", "Gilliam", "Grant", "Harney", "Hood River", "Jackson", "Jefferson",
    "Josephine", "Klamath", "Lake", "Lane", "Lincoln", "Linn", "Malheur", "Marion",
    "Morrow", "Multnomah", "Polk", "Sherman", "Tillamook", "Umatilla", "Union", "Wallowa",
    "Wasco", "Washington", "Wheeler", "Yamhill"
]

def run():
    for name in OREGON_COUNTIES:
        county, created = County.objects.get_or_create(name=name)
        if created:
            print(f"✔ Created county: {name}")
        else:
            print(f"↪ County already exists: {name}")
