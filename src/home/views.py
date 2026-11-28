from django.shortcuts import render


LOCATIONS = [
    {
        "slug": "gku-2",
        "name": "GKU 2",
        "description": "Kantin di area Gedung Kuliah Umum 2.",
        "icon": "🏢",
    },
    {
        "slug": "koica",
        "name": "Koica",
        "description": "Pilihan kantin di area Koica.",
        "icon": "🏬",
    },
    {
        "slug": "asrama-tb-2",
        "name": "Asrama TB 2",
        "description": "Kantin untuk area Asrama TB 2.",
        "icon": "🏠",
    },
    {
        "slug": "asrama-tb-3",
        "name": "Asrama TB 3",
        "description": "Kantin untuk area Asrama TB 3.",
        "icon": "🏡",
    },
]


def index(request):
    selected_slug = request.GET.get("kantin")
    selected_location = next(
        (location for location in LOCATIONS if location["slug"] == selected_slug),
        None,
    )
    locations = [
        {**location, "selected": location is selected_location}
        for location in LOCATIONS
    ]
    return render(
        request,
        "home/index.html",
        {
            "locations": locations,
            "selected_location": selected_location,
        },
    )