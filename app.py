
import io
import random
import textwrap

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter

st.set_page_config(
    page_title="Lyric2Poster",
    page_icon="✦",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

.stApp {
    background: #0c0c10;
    color: #f5f2fa;
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    max-width: 1350px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label {
    color: #f5f2fa;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #18171f;
    color: #ffffff;
    border: 1px solid #393542;
    border-radius: 10px;
}
div[data-testid="stSelectbox"] > div > div {
    background: #18171f;
}
div.stButton > button,
div.stDownloadButton > button {
    border-radius: 10px;
    min-height: 45px;
    border: 1px solid #b9a5ff;
    background: #b9a5ff;
    color: #15121d;
    font-weight: 700;
}
div.stDownloadButton > button:hover {
    background: #d1c5ff;
    border-color: #d1c5ff;
    color: #15121d;
}
div[data-testid="stFileUploader"] {
    background: #18171f;
    border-radius: 10px;
    padding: 10px;
}
.small-note {
    color: #aaa3b8;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='letter-spacing:5px;color:#b9a5ff;font-size:12px;'>"
    "MUSIC × VISUAL EXPERIMENTS</p>",
    unsafe_allow_html=True
)
st.title("Lyric2Poster")
st.markdown(
    "<p class='small-note'>Turn the atmosphere of a song into a visual artwork.</p>",
    unsafe_allow_html=True
)

st.divider()

def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

def get_font(size, bold=False):
    candidates = (
        ["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

def fit_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return "\n".join(lines)

def make_poster(title, artist, lyrics, style, layout,
                bg_hex, accent_hex, grain, uploaded):
    W, H = 900, 1200
    bg = hex_to_rgb(bg_hex)
    accent = hex_to_rgb(accent_hex)

    # Gradient background
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / max(1, H - 1)
        shade = 0.12 * t
        color = tuple(
            int(max(0, min(255, c * (1 - shade) + 12 * t)))
            for c in bg
        )
        arr[y, :, :] = color

    image = Image.fromarray(arr).convert("RGB")

    if uploaded is not None:
        try:
            uploaded.seek(0)
            overlay = Image.open(uploaded).convert("RGB")
            overlay.thumbnail((W, H))
            canvas = Image.new("RGB", (W, H), bg)
            x = (W - overlay.width) // 2
            y = (H - overlay.height) // 2
            canvas.paste(overlay, (x, y))
            image = Image.blend(image, canvas, 0.55)
        except Exception:
            pass

    draw = ImageDraw.Draw(image, "RGBA")

    # Decorative art direction
    if style == "Chrome / Cyber":
        for r in range(90, 390, 35):
            draw.ellipse(
                (W // 2 - r, 370 - r, W // 2 + r, 370 + r),
                outline=(*accent, 125),
                width=2
            )
        draw.ellipse(
            (265, 210, 635, 580),
            fill=(*accent, 28)
        )
        for x in range(70, W, 70):
            draw.line((x, 130, x, 600), fill=(*accent, 18), width=1)

    elif style == "Dream Blur":
        art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        art_draw = ImageDraw.Draw(art, "RGBA")
        rng = random.Random(12)
        for _ in range(38):
            x = rng.randint(0, W)
            y = rng.randint(100, 800)
            r = rng.randint(25, 110)
            art_draw.ellipse(
                (x-r, y-r, x+r, y+r),
                fill=(*accent, 24)
            )
        art = art.filter(ImageFilter.GaussianBlur(24))
        image = Image.alpha_composite(image.convert("RGBA"), art).convert("RGB")
        draw = ImageDraw.Draw(image, "RGBA")

    elif style == "Raw Underground":
        rng = random.Random(24)
        for _ in range(55):
            x = rng.randint(0, W)
            y = rng.randint(100, 900)
            length = rng.randint(15, 180)
            draw.line(
                (x, y, min(W, x + length), y),
                fill=(*accent, rng.randint(35, 140)),
                width=rng.randint(1, 4)
            )
        for _ in range(12):
            y = rng.randint(100, 900)
            draw.rectangle(
                (0, y, W, y + rng.randint(1, 5)),
                fill=(255, 255, 255, 12)
            )

    # Typography
    title_font = get_font(76, bold=True)
    artist_font = get_font(29)
    lyric_font = get_font(27)
    tiny_font = get_font(16)

    if layout == "Centered":
        anchor_x = W // 2
        title_anchor = "mt"
        text_align = "center"
    elif layout == "Left aligned":
        anchor_x = 72
        title_anchor = "lt"
        text_align = "left"
    else:
        anchor_x = 95
        title_anchor = "lt"
        text_align = "left"

    if style == "Minimal Type":
        title_y = 430
        draw.line((72, 180, 180, 180), fill=(*accent, 255), width=4)
        draw.text(
            (72, 205), "A STUDY IN SOUND",
            font=tiny_font, fill=(*accent, 255)
        )
    elif style == "Dream Blur":
        title_y = 680
    else:
        title_y = 650

    title = title.strip() or "UNTITLED"
    artist = artist.strip() or "UNKNOWN ARTIST"

    title_display = title.upper()
    max_title_width = W - 120
    title_lines = fit_text(title_display, title_font, max_title_width, draw)

    draw.multiline_text(
        (anchor_x, title_y),
        title_lines,
        font=title_font,
        fill=(250, 247, 255, 255),
        spacing=4,
        anchor=title_anchor,
        align=text_align
    )

    title_height = draw.multiline_textbbox(
        (anchor_x, title_y),
        title_lines,
        font=title_font,
        spacing=4,
        anchor=title_anchor,
        align=text_align
    )[3] - draw.multiline_textbbox(
        (anchor_x, title_y),
        title_lines,
        font=title_font,
        spacing=4,
        anchor=title_anchor,
        align=text_align
    )[1]

    artist_y = title_y + title_height + 26
    draw.text(
        (anchor_x, artist_y),
        artist,
        font=artist_font,
        fill=(*accent, 255),
        anchor="mt" if text_align == "center" else "lt"
    )

    if lyrics.strip():
        lyric_y = artist_y + 85
        excerpt = fit_text(
            lyrics.strip(),
            lyric_font,
            620,
            draw
        )

        # Use supported anchors for multiline text:
        # "ma" centers the block; "la" aligns it to the left.
        if text_align == "center":
            draw.multiline_text(
                (W // 2, lyric_y),
                excerpt,
                font=lyric_font,
                fill=(246, 241, 252, 235),
                spacing=12,
                anchor="ma",
                align="center"
            )
        else:
            draw.multiline_text(
                (anchor_x, lyric_y),
                excerpt,
                font=lyric_font,
                fill=(246, 241, 252, 235),
                spacing=12,
                anchor="la",
                align="left"
            )

    # Footer and small design details
    draw.line(
        (72, H - 105, W - 72, H - 105),
        fill=(*accent, 100),
        width=1
    )
    draw.text(
        (72, H - 78),
        "SOUND → IMAGE",
        font=tiny_font,
        fill=(235, 229, 245, 190)
    )
    draw.text(
        (W - 72, H - 78),
        "LYRIC2POSTER  /  001",
        font=tiny_font,
        fill=(*accent, 230),
        anchor="ra"
    )

    # Film grain
    if grain > 0:
        rng = np.random.default_rng(7)
        pixels = np.asarray(image).astype(np.int16)
        noise = rng.normal(0, grain * 0.22, (H, W, 1))
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        image = Image.fromarray(pixels)

    return image

with st.container():
    controls, preview = st.columns([0.9, 1.1], gap="large")

    with controls:
        st.subheader("01 / Your song")

        title = st.text_input("Song title", value="jeans")
        artist = st.text_input("Artist", value="2hollis")
        lyrics = st.text_area(
            "Your lyric excerpt",
            value="type your favorite lyric here",
            height=130,
            help="Use a short lyric excerpt you provide yourself."
        )

        st.subheader("02 / Art direction")

        style = st.selectbox(
            "Visual style",
            [
                "Chrome / Cyber",
                "Dream Blur",
                "Minimal Type",
                "Raw Underground"
            ]
        )

        layout = st.selectbox(
            "Composition",
            ["Centered", "Left aligned", "Experimental"]
        )

        bg_hex = st.color_picker("Background", "#17151F")
        accent_hex = st.color_picker("Accent", "#B9A5FF")
        grain = st.slider("Film grain", 0, 100, 25)

        uploaded = st.file_uploader(
            "Upload a background image (optional)",
            type=["png", "jpg", "jpeg"]
        )

    with preview:
        st.subheader("03 / Poster preview")

        try:
            poster = make_poster(
                title, artist, lyrics, style, layout,
                bg_hex, accent_hex, grain, uploaded
            )

            st.image(poster, use_container_width=True)

            output = io.BytesIO()
            poster.save(output, format="PNG")
            output.seek(0)

            safe_name = "".join(
                c if c.isalnum() or c in "-_" else "_"
                for c in (title.strip() or "poster")
            )

            st.download_button(
                "↓  Download poster as PNG",
                data=output.getvalue(),
                file_name=f"{safe_name}_poster.png",
                mime="image/png",
                use_container_width=True
            )

            st.caption(
                "Experiment with typography, color and texture "
                "to create your own visual identity."
            )

        except Exception as error:
            st.error("The poster could not be generated.")
            st.code(str(error))
            st.info(
                "Try a shorter title or lyric excerpt. "
                "If the issue continues, send me the error message."
            )

st.divider()
st.markdown(
    "<p style='text-align:center;color:#777181;font-size:12px;'>"
    "LYRIC2POSTER · AN EXPERIMENT IN MUSIC AND VISUAL DESIGN"
    "</p>",
    unsafe_allow_html=True
)

