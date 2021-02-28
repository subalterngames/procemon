from procemon import Dex

"""
Make sure that there are enough valid nouns per monster type.
"""

num_types = len(Dex.get_all_types())
num_monsters_per_type = 9
dex = Dex(num_types=num_types, num_monsters_per_type=9)
print("Monster types with too few images:")
for m in dex.types:
    images = dex.get_images(monster_type=m)
    if len(images) < num_monsters_per_type:
        print(m, len(images), images)
