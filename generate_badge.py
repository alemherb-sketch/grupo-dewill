import math

cx, cy = 50, 50
outer_r = 50
inner_r = 44
points = 18

path_data = []
for i in range(points * 2):
    angle = math.pi * i / points
    r = outer_r if i % 2 == 0 else inner_r
    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)
    
    if i == 0:
        path_data.append(f"M {x:.1f} {y:.1f}")
    else:
        path_data.append(f"L {x:.1f} {y:.1f}")

path_str = " ".join(path_data) + " Z"

svg = f'''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="{path_str}" fill="#0A1931" />
</svg>'''

with open('static/assets/badge-bg.svg', 'w') as f:
    f.write(svg)
print("SVG generated")
