from PIL import Image
import numpy as np

# Load scrambled image
img = Image.open("jigsaw.webp").convert("RGB")

w, h = img.size
tile_w = w // 5
tile_h = h // 5

# Mapping:
# (scrambled_row, scrambled_col) -> (original_row, original_col)
mapping = {
    (0, 0): (2, 1),
    (0, 1): (1, 1),
    (0, 2): (4, 1),
    (0, 3): (0, 3),
    (0, 4): (0, 1),
    (1, 0): (1, 4),
    (1, 1): (2, 0),
    (1, 2): (2, 4),
    (1, 3): (4, 2),
    (1, 4): (2, 2),
    (2, 0): (0, 0),
    (2, 1): (3, 2),
    (2, 2): (4, 3),
    (2, 3): (3, 0),
    (2, 4): (3, 4),
    (3, 0): (1, 0),
    (3, 1): (2, 3),
    (3, 2): (3, 3),
    (3, 3): (4, 4),
    (3, 4): (0, 2),
    (4, 0): (3, 1),
    (4, 1): (1, 2),
    (4, 2): (1, 3),
    (4, 3): (0, 4),
    (4, 4): (4, 0),
}

# Reconstruct
reconstructed = Image.new("RGB", (w, h))

# for (sr, sc), (orow, ocol) in mapping.items():
#     tile = img.crop((sc * tile_w, sr * tile_h, (sc + 1) * tile_w, (sr + 1) * tile_h))

#     reconstructed.paste(tile, (ocol * tile_w, orow * tile_h))

for (sr, sc), (orow, ocol) in mapping.items():
    tile = img.crop(
        (ocol * tile_w, orow * tile_h, (ocol + 1) * tile_w, (orow + 1) * tile_h)
    )
    reconstructed.paste(tile, (sc * tile_w, sr * tile_h))
# Exact luminance grayscale
rgb = np.asarray(reconstructed).astype(np.float64)

gray = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

# Important: round, don't floor
# gray = np.rint(gray).clip(0, 255).astype(np.uint8)

gray = gray.astype(np.uint8)

gray_img = Image.fromarray(gray, mode="L")

# Save losslessly
gray_img.save("answer.png")
