
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import random
import io
import textwrap

st.set_page_config(page_title="Lyric2Poster", page_icon="✦", layout="wide")

st.markdown("""
<style>
.stApp {
    background: #101014;
    color: #f5f2f7;
}
h1, h2, h3 { color: #f5f2f7; }
section[data-testid="stSidebar"] {
    background: #19191f;
}
div.stButton > button, div.stDownloadButton > button {
    border-radius: 8px;
    border: 1px solid #aaa0bd;
}
</style>
""", unsafe_allow_html=True)

st.title("✦ Lyric2Poster")
st.caption("Turn a song's atmosphere into a visual poster.")

left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("01 — Your song")
    title = st.text_input("Song title", "jeans")
    artist = st.text_input("Artist", "2hollis")
    lyrics = st.text_area(
        "Your lyric excerpt",
        "type your favorite lyric here",
        height=120,
        help="Paste a short excerpt that you provide yourself."
    )

    st.subheader("02 — Art direction")
    style = st.selectbox(
        "Visual style",
        ["Chrome / Cyber", "Dream Blur", "Minimal Type", "Raw Underground"]
    )
    layout = st.selectbox(
        "Composition",
        ["Centered", "Left aligned", "Experimental"]
    )
    background_color = st.color_picker("Background color", "#17151F")
    accent_color = st.color_picker("Accent color", "#B8A5FF")
    grain = st.slider("Film grain", 0, 100, 25)
    uploaded = st.file_uploader(
        "Optional background image",
        type=["png", "jpg", "jpeg"]
    )

def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

def make_poster():
    W, H = 900, 1200
    bg = hex_rgb(background_color)
    accent = hex_rgb(accent_color)

    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        color = tuple(int(bg[i] * (1-t) + min(255, bg[i] + 28) * t)
                      for i in range(3))
        arr[y, :, :] = color
    image = Image.fromarray(arr).convert("RGB")

    if uploaded is not None:
        try:
            overlay = Image.open(uploaded).convert("RGB")
            overlay = overlay.resize((W, H)).filter(ImageFilter.GaussianBlur(2))
            overlay = Image.blend(image, overlay, 0.45)
            image = overlay
        except Exception:
            pass

    draw = ImageDraw.Draw(image, "RGBA")

    if style == "Chrome / Cyber":
        for r in range(100, 430, 35):
            draw.ellipse(
                (W//2-r, 390-r, W//2+r, 390+r),
                outline=(*accent, 100), width=2
            )
        draw.ellipse((250, 220, 650, 620), fill=(*accent, 35))
        image = image.filter(ImageFilter.GaussianBlur(0.6))

    elif style == "Dream Blur":
        for _ in range(35):
            x = random.randint(-100, W)
            y = random.randint(100, 850)
            r = random.randint(20, 100)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=(*accent, 22))
        image = image.filter(ImageFilter.GaussianBlur(20))
        draw = ImageDraw.Draw(image, "RGBA")

    elif style == "Raw Underground":
        for _ in range(45):
            x = random.randint(0, W)
            y = random.randint(100, H)
            draw.line((x, y, x + random.randint(-100, 100), y),
                      fill=(*accent, 100), width=random.randint(1, 4))

    if layout == "Centered":
        align = "center"
        anchor_x = W // 2
    elif layout == "Left aligned":
        align = "left"
        anchor_x = 75
    else:
        align = "left"
        anchor_x = random.choice([70, 150, 230])

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 76)
        font_artist = ImageFont.truetype("DejaVuSans.ttf", 30)
        font_lyric = ImageFont.truetype("DejaVuSans.ttf", 29)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 17)
    except OSError:
        font_title = ImageFont.load_default()
        font_artist = font_title
        font_lyric = font_title
        font_small = font_title

    text_color = (248, 244, 255, 255)
    title_y = 720 if style != "Minimal Type" else 500

    if style == "Minimal Type":
        draw.line((75, 160, 180, 160), fill=(*accent, 255), width=4)
        draw.text((75, 190), "A SONG POSTER", font=font_small,
                  fill=(*accent, 255))

    draw.text((anchor_x, title_y), title.upper(), font=font_title,
              fill=text_color, anchor= "mt" if align == "center" else None)

    artist_y = title_y + 105
    draw.text((anchor_x, artist_y), artist, font=font_artist,
              fill=(*accent, 255),
              anchor="mt" if align == "center" else None)

    if lyrics.strip():
        excerpt = textwrap.fill(lyrics.strip(), width=32)
        lyric_y = artist_y + 100
        draw.multiline_text(
            (anchor_x, lyric_y), excerpt, font=font_lyric,
            fill=text_color, spacing=12,
            anchor="mt" if align == "center" else None,
            align=align
        )

    draw.text((W-70, H-65), "LYRIC2POSTER  /  001",
              font=font_small, fill=(*accent, 220), anchor="rs")
    draw.text((70, H-65), "SOUND → IMAGE",
              font=font_small, fill=(255, 255, 255, 170))

    if grain > 0:
        rng = np.random.default_rng(7)
        pixels = np.array(image).astype(np.int16)
        noise = rng.normal(0, grain * 0.22, pixels.shape[:2])
        pixels = np.clip(pixels + noise[:, :, None], 0, 255).astype(np.uint8)
        image = Image.fromarray(pixels)

    return image

with right:
    st.subheader("03 — Live poster preview")
    poster = make_poster()
    st.image(poster, use_container_width=True)
    buffer = io.BytesIO()
    poster.save(buffer, format="PNG")
    st.download_button(
        "Download poster as PNG",
        data=buffer.getvalue(),
        file_name="lyric2poster.png",
        mime="image/png",
        use_container_width=True
    )
    st.caption("Tip: experiment with color, grain and composition to create your own visual identity.")
