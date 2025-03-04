import images
import random
from PIL import Image, ImageDraw, ImageFont, ImageChops

FONTSIZE = 25
FONT = ImageFont.truetype("ASCII-art\DejaVuSansMono-Bold.ttf", FONTSIZE)
LINEHEIGHT = 25
CHARWIDTH = 15


def draw_art(art):
    background = art["background"]
    w, h, lines, chars = art["dimensions"]

    img = Image.new("RGB", (w, h), background)
    draw = ImageDraw.Draw(img, "RGB")

    for i in range(lines):
        for j in range(chars):
            letter = art["letters"][i*chars+j]
            color = art["colors"][i*chars+j]
            x, y = j * CHARWIDTH, i * LINEHEIGHT
            draw.text((x, y), letter, fill=color, anchor="lt", font=FONT)

    return img


def calculate_img_diff(img1, img2):
    diff_img = ImageChops.difference(img1, img2)
    total_diff = sum((x+y+z) for (x, y, z) in diff_img.getdata())
    return total_diff


def evaluate_art(art, img):
    art_img = draw_art(art)
    return calculate_img_diff(img, art_img)


def evaluate_letter(img_crop, background, letter, color):
    art_img = Image.new("RGB", (CHARWIDTH, LINEHEIGHT), background)
    draw = ImageDraw.Draw(art_img, "RGB")
    draw.text((0, 0), letter, fill=color, anchor="lt", font=FONT)
    return calculate_img_diff(img_crop, art_img)


def optimize_letter(art, img, line, char):
    background = art["background"]
    _, _, _, chars = art["dimensions"]
    n = line * chars + char

    # calculate subsection
    top, left = line * LINEHEIGHT, char * CHARWIDTH
    bot, right = top + LINEHEIGHT, left + CHARWIDTH
    img_crop = img.crop((left, top, right, bot))

    # Initial values, used for scoring
    letter = art["letters"][n]
    color = art["colors"][n]

    score = evaluate_letter(img_crop, background, letter, color)
    for letter in art["letter_pool"]:
        for color in art["color_pool"]:
            try_score = evaluate_letter(img_crop, background, letter, color)
            if try_score < score:
                art["letters"][n] = letter
                art["colors"][n] = color
                score = try_score
    return


def generate_ascii(path, letter_pool, report=True, out_file="ascii.jpg",
                   color_pool=[(0, 0, 0)], background=(255, 255, 255)):
    img = Image.open(path)
    w, h = img.size

    chars = w // CHARWIDTH
    lines = h // LINEHEIGHT

    art = {"dimensions": (w, h, lines, chars), "background": background,
           "letters": [letter_pool[0] for _ in range(chars*lines)],
           "letter_pool": letter_pool,
           "color_pool": color_pool,
           "colors": [color_pool[0] for _ in range(chars*lines)]}

    for l in range(lines):
        for c in range(chars):
            optimize_letter(art, img, l, c)
        if report:
            print(f"Line {l} out of {lines} done.")

    art_img = draw_art(art)
    art_img.save(out_file)