from txtdsl import parse_patch, render_patch

schematic = open("./jan-24-patch.txt").read()
patch = parse_patch(schematic)
render_patch(patch)
