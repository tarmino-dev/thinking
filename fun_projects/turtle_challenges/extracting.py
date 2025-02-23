import colorgram

colors = colorgram.extract('image.jpg', 30)

"""Extracting colors from images. 3 ways of accessing fields of NamedTuple."""

color_list1 = [] # for accessing fields by index
color_list2 = [] # for alternative way of accessing fields by keyname
color_list3 = [] # for alternative way of accessing fields using getattr()

for color in colors:
    color_list1.append((color.rgb[0], color.rgb[1], color.rgb[2])) # by index
    color_list2.append((color.rgb.r, color.rgb.g, color.rgb.b)) # by keyname
    color_list3.append((getattr(color.rgb, "r"), getattr(color.rgb, "g"), getattr(color.rgb, "b"))) # using getattr()

print(color_list1)
print(color_list2)
print(color_list3)
