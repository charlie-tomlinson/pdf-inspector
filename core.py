from typing import Literal, Dict, Iterable
import base64
import pymupdf
from PIL import Image
import io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import plotly.graph_objects as go

COLORS = {
    "blocks": (1, 0, 0),
    "lines": (0, 0, 1),
    "spans": (0, 1, 0),
    "words": (1, 0.5, 0),
}

FLAG_MAP = {
    "text_preserve_ligatures": pymupdf.TEXT_PRESERVE_LIGATURES,
    "text_preserve_whitespace": pymupdf.TEXT_PRESERVE_WHITESPACE,
    "text_preserve_images": pymupdf.TEXT_PRESERVE_IMAGES,
    "text_inhibit_spaces": pymupdf.TEXT_INHIBIT_SPACES,
    "text_dehyphenate": pymupdf.TEXT_DEHYPHENATE,
    "text_preserve_spans": pymupdf.TEXT_PRESERVE_SPANS,
    "text_mediabox_clip": pymupdf.TEXT_MEDIABOX_CLIP,
    "text_use_cid_for_unknown_unicode": pymupdf.TEXT_USE_CID_FOR_UNKNOWN_UNICODE,
    "text_accurate_bboxes": pymupdf.TEXT_ACCURATE_BBOXES,
    "text_ignore_actualtext": pymupdf.TEXT_IGNORE_ACTUALTEXT,
    "text_segment": pymupdf.TEXT_SEGMENT,
}

def init_docs(uploads: Iterable, dpi: int = 450) -> list[dict]:
    """
    Initialize document and page records from uploaded PDFs.

    - Renders each page to a PIL image at the given DPI.
    - Stores immutable PDF bytes once per document.
    - Initializes page-level extraction slots as None.

    Returns a list of document dicts sorted by name.
    """
    docs: list[dict] = []

    for file in uploads:
        pdf_bytes = file.getvalue()
        pages: list[dict] = []

        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            for page in pdf:
                pix = page.get_pixmap(dpi=dpi)
                png_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(png_bytes))

                pages.append(
                    {
                        "image": img,
                        "blocks": None,
                        "lines": None,
                        "spans": None,
                        "words": None,
                    }
                )

        docs.append(
            {
                "name": file.name,
                "bytes": pdf_bytes,
                "pages": pages,
            }
        )

    docs.sort(key=lambda d: d["name"])
    return docs


def resolve_text_flags(state: dict) -> int:
    """
    Resolve Streamlit boolean session state flags into a PyMuPDF flag integer.
    Every flag is explicitly enabled or explicitly disabled.
    """
    flags = 0

    for key, flag in FLAG_MAP.items():
        enabled = bool(state.get(key, False))
        if enabled:
            flags |= flag
        else:
            flags &= ~flag

    return flags


def get_textpage(
    pdf_bytes: bytes,
    page_index: int,
    flags: int,
    ocr_mode: Literal["off", "auto", "full"],
) -> pymupdf.TextPage:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        page = pdf[page_index]

        if ocr_mode == "off":
            return page.get_textpage(flags=flags)

        if ocr_mode == "auto":
            return page.get_textpage_ocr(flags=flags)

        if ocr_mode == "full":
            return page.get_textpage_ocr(flags=flags, full=True)

    raise ValueError(f"Invalid ocr_mode: {ocr_mode}")

def extract_rects(textpage: pymupdf.TextPage) -> Dict[str, list[pymupdf.Rect]]:
    """
    Extract bounding boxes from a TextPage, normalized to page coordinates.

    Returns a dict with keys: blocks, lines, spans, words.
    """
    out: Dict[str, list[pymupdf.Rect]] = {}

    d = textpage.extractDICT(sort=True)

    out["blocks"] = [
        pymupdf.Rect(b["bbox"])
        for b in d.get("blocks", [])
        if "bbox" in b
    ]

    out["lines"] = [
        pymupdf.Rect(line["bbox"])
        for block in d.get("blocks", [])
        for line in block.get("lines", [])
        if "bbox" in line
    ]

    out["spans"] = [
        pymupdf.Rect(span["bbox"])
        for block in d.get("blocks", [])
        for line in block.get("lines", [])
        for span in line.get("spans", [])
        if "bbox" in span
    ]

    out["words"] = [
        pymupdf.Rect(w[0], w[1], w[2], w[3])
        for w in textpage.extractWORDS()
    ]

    return out


# --- Helper functions ---

def rects_to_pixels(
    rects: Iterable[pymupdf.Rect],
    dpi: int,
) -> list[tuple[float, float, float, float]]:
    """
    Convert page-space rects (points) to pixel-space tuples.
    """
    scale = dpi / 72
    return [
        (r.x0 * scale, r.y0 * scale, r.x1 * scale, r.y1 * scale)
        for r in rects
    ]


def render_page_figure(
    image: Image.Image,
    rects: Iterable[pymupdf.Rect] | None,
    dpi: int,
    *,
    facecolor: str = "yellow",
    edgecolor: str = "red",
    alpha: float = 0.3,
):
    """
    Render a page image with optional highlighted rectangles.

    Returns a matplotlib Figure. No state is mutated.
    """
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.set_xlim(0, image.width)
    ax.set_ylim(image.height, 0)
    ax.axis("off")

    if rects:
        for x0, y0, x1, y1 in rects_to_pixels(rects, dpi):
            ax.add_patch(
                Rectangle(
                    (x0, y0),
                    x1 - x0,
                    y1 - y0,
                    facecolor=facecolor,
                    edgecolor=edgecolor,
                    alpha=alpha,
                    linewidth=1,
                )
            )

    return fig


def render_page_plotly(
    image: Image.Image,
    rects: Iterable[pymupdf.Rect] | None,
    dpi: int,
    *,
    level: str | None = None,
):
    """
    Render a page image with highlighted rectangles using Plotly for interactivity.
    """
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    img_bytes = buf.read()
    img_uri = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"

    width_px = image.width
    height_px = image.height
    dpi = max(dpi, 1)
    page_width = width_px * 72 / dpi
    page_height = height_px * 72 / dpi

    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=img_uri,
            xref="x",
            yref="y",
            x=0,
            y=0,
            sizex=page_width,
            sizey=page_height,
            sizing="stretch",
            xanchor="left",
            yanchor="top",
            layer="below",
        )
    )

    if rects:
        color = COLORS.get(level or "", (1, 0, 0))
        fill = f"rgba({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)},0.35)"
        for r in rects:
            fig.add_shape(
                type="rect",
                x0=r.x0,
                y0=r.y0,
                x1=r.x1,
                y1=r.y1,
                xref="x",
                yref="y",
                line=dict(color="rgba(0,0,0,0)", width=0),
                fillcolor=fill,
                opacity=0.6,
            )

    fig.update_xaxes(
        range=[0, page_width],
        autorange=False,
        constrain="range",
        showgrid=False,
        zeroline=False,
        fixedrange=False,
        tickformat=".0f",
        ticks="outside",
        ticklen=6,
        tickwidth=1,
        tickcolor="white",
        tickfont=dict(color="white"),
        minallowed=0,
        maxallowed=page_width,
    )

    fig.update_yaxes(
        range=[page_height, 0],
        autorange=False,
        constrain="range",
        showgrid=False,
        zeroline=False,
        fixedrange=False,
        scaleanchor="x",
        scaleratio=1,
        tickformat=".0f",
        ticks="outside",
        ticklen=6,
        tickwidth=1,
        tickcolor="white",
        tickfont=dict(color="white"),
        minallowed=0,
        maxallowed=page_height,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        dragmode="zoom",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        autosize=False,
        width=int(page_width),
        height=int(page_height),
        xaxis_range=[0, page_width],
        yaxis_range=[page_height, 0],
    )

    return fig
