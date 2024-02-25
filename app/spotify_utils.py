def print_playlist_structure(data, indent=2):
    for key, value in data.items():
        print(" " * indent + f"{key}: {type(value)}")
        if isinstance(value, dict):
            print_playlist_structure(value, indent + 2)

def print_playlist_items_structure(items, indent=0, file=None):
    for item in items:
        if isinstance(item, dict):
            for key, value in item.items():
                print('  ' * indent + str(key) + ':', type(value), file=file)
                if isinstance(value, dict):
                    print_playlist_items_structure([value], indent + 1, file=file)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    print_playlist_items_structure(value, indent + 1, file=file)

def print_cover_image_structure(cover_image):
    print("Cover Image Structure:")
    for item in cover_image:
        print(f"{type(item)}")
        for key, value in item.items():
            print(f"  {key}: {type(value)}")
    #     print(type(item).__name__)
    #     print(f"  {item}: {type(item).__name__}")
