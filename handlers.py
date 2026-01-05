import streamlit as st

import core

LEVELS = ["blocks", "lines", "spans", "words"]

def init_helper_states():

    if "docs" not in st.session_state:
        st.session_state.docs = []

    if "doc_idx" not in st.session_state:
        st.session_state.doc_idx = None

    if "doc_name" not in st.session_state:
        st.session_state.doc_name = None

    if "page_index" not in st.session_state:
        st.session_state.page_index = 0

    if "dpi" not in st.session_state:
        st.session_state.dpi = 450

    if "level_select" not in st.session_state:
        st.session_state.level_select = LEVELS[0]

    if "last_flags" not in st.session_state:
        st.session_state.last_flags = None

    if "last_ocr_mode" not in st.session_state:
        st.session_state.last_ocr_mode = None


def reconcile_docs():
    uploads = st.session_state.get("uploads") or []
    upload_names = {f.name for f in uploads}

    docs = [
        d for d in st.session_state.docs
        if d["name"] in upload_names
    ]

    st.session_state.docs = docs

    if not docs:
        st.session_state.doc_idx = None
        st.session_state.doc_name = None
        st.session_state.page_index = None
        return

    idx = st.session_state.doc_idx or 0
    idx = min(idx, len(docs) - 1)

    st.session_state.doc_idx = idx
    st.session_state.doc_name = docs[idx]["name"]
    current_page = st.session_state.get("page_index")
    if current_page is None:
        st.session_state.page_index = 0
    else:
        st.session_state.page_index = max(0, min(current_page, len(docs[idx]["pages"]) - 1))


def on_upload():
    uploads = st.session_state.uploads or []
    
    with st.spinner(text="Converting Files...", show_time=True):
        docs = core.init_docs(uploads, dpi=st.session_state.dpi)

    st.session_state.docs = docs
    st.session_state.last_flags = None
    st.session_state.last_ocr_mode = None
    st.session_state.page_index = 0

    if docs:
        st.session_state.doc_idx = 0
        st.session_state.doc_name = docs[0]["name"]
    else:
        st.session_state.doc_idx = None
        st.session_state.doc_name = None
        st.session_state.page_index = None


def on_doc_change():
    name = st.session_state.doc_name
    if not name:
        st.session_state.doc_idx = None
        return

    for i, d in enumerate(st.session_state.docs):
        if d["name"] == name:
            st.session_state.doc_idx = i
            st.session_state.page_index = 0   # reset page cursor
            return


def docs():
    return st.session_state.docs


def doc_names():
    return [d["name"] for d in st.session_state.docs]


def current_doc():
    idx = st.session_state.doc_idx
    if idx is None or not st.session_state.docs:
        return None
    return st.session_state.docs[idx]


def doc_prev_disabled() -> bool:
    idx = st.session_state.doc_idx
    return idx is None or idx <= 0


def doc_next_disabled() -> bool:
    idx = st.session_state.doc_idx
    return idx is None or idx >= len(st.session_state.docs) - 1


def on_doc_next():
    idx = st.session_state.doc_idx
    if idx < len(st.session_state.docs) - 1:
        st.session_state.doc_idx = idx + 1
        st.session_state.doc_name = st.session_state.docs[idx + 1]["name"]
        st.session_state.page_index = 0


def on_doc_prev():
    idx = st.session_state.doc_idx
    if idx > 0:
        st.session_state.doc_idx = idx - 1
        st.session_state.doc_name = st.session_state.docs[idx - 1]["name"]
        st.session_state.page_index = 0


def page_indices():
    doc = current_doc()
    if not doc:
        return []
    return list(range(len(doc["pages"])))


def page_prev_disabled() -> bool:
    idx = st.session_state.page_index
    return idx is None or idx <= 0


def page_next_disabled() -> bool:
    idx = st.session_state.page_index
    doc = current_doc()
    if idx is None or not doc:
        return True
    return idx >= len(doc["pages"]) - 1


def on_page_prev():
    idx = st.session_state.page_index
    if idx is not None and idx > 0:
        st.session_state.page_index = idx - 1


def on_page_next():
    idx = st.session_state.page_index
    doc = current_doc()
    if idx is not None and doc and idx < len(doc["pages"]) - 1:
        st.session_state.page_index = idx + 1


def level_index():
    level = st.session_state.get("level_select")
    if level not in LEVELS:
        return None
    return LEVELS.index(level)


def level_prev_disabled() -> bool:
    idx = level_index()
    return idx is None or idx <= 0


def level_next_disabled() -> bool:
    idx = level_index()
    return idx is None or idx >= len(LEVELS) - 1


def on_level_prev():
    idx = level_index()
    if idx is not None and idx > 0:
        st.session_state.level_select = LEVELS[idx - 1]


def on_level_next():
    idx = level_index()
    if idx is not None and idx < len(LEVELS) - 1:
        st.session_state.level_select = LEVELS[idx + 1]


def current_flags() -> int:
    return core.resolve_text_flags(st.session_state)


def current_ocr_mode() -> str:
    return st.session_state.get("ocr_mode", "off")


def current_dpi() -> int:
    return int(st.session_state.get("dpi", 450))


def invalidate_boxes_if_needed(flags: int, ocr_mode: str) -> None:
    if (
        st.session_state.last_flags == flags
        and st.session_state.last_ocr_mode == ocr_mode
    ):
        return

    for doc in st.session_state.docs:
        for page in doc["pages"]:
            page["blocks"] = None
            page["lines"] = None
            page["spans"] = None
            page["words"] = None

    st.session_state.last_flags = flags
    st.session_state.last_ocr_mode = ocr_mode


def ensure_boxes_for_doc(doc: dict, flags: int, ocr_mode: str) -> None:
    for i, page in enumerate(doc["pages"]):
        if page["blocks"] is not None:
            continue

        textpage = core.get_textpage(
            pdf_bytes=doc["bytes"],
            page_index=i,
            flags=flags,
            ocr_mode=ocr_mode,
        )
        rects = core.extract_rects(textpage)

        page["blocks"] = rects["blocks"]
        page["lines"] = rects["lines"]
        page["spans"] = rects["spans"]
        page["words"] = rects["words"]


def warm_boxes(flags: int, ocr_mode: str) -> None:
    doc = current_doc()
    if not doc:
        return

    ensure_boxes_for_doc(doc, flags, ocr_mode)

    idx = st.session_state.doc_idx
    docs = st.session_state.docs
    if idx is None:
        return

    next_idx = idx + 1
    if 0 <= next_idx < len(docs):
        ensure_boxes_for_doc(docs[next_idx], flags, ocr_mode)


def current_page_figure(flags: int, ocr_mode: str, dpi: int):
    doc = current_doc()
    page_index = st.session_state.get("page_index")
    if doc is None or page_index is None:
        return None

    invalidate_boxes_if_needed(flags, ocr_mode)
    warm_boxes(flags, ocr_mode)

    if page_index < 0 or page_index >= len(doc["pages"]):
        return None

    page = doc["pages"][page_index]
    level = st.session_state.get("level_select")
    if level not in page:
        return None

    rects = page[level]
    fig = core.render_page_plotly(page["image"], rects, dpi, level=level)
    return fig


def on_dpi_change():
    uploads = st.session_state.get("uploads") or []
    dpi = st.session_state.get("dpi", 450)

    st.session_state.last_flags = None
    st.session_state.last_ocr_mode = None

    if not uploads:
        st.session_state.docs = []
        st.session_state.doc_idx = None
        st.session_state.doc_name = None
        st.session_state.page_index = None
        return

    current_name = st.session_state.doc_name
    current_page = st.session_state.get("page_index")

    with st.spinner(text=f"Re-rendering at {dpi} DPI...", show_time=True):
        docs = core.init_docs(uploads, dpi=dpi)

    st.session_state.docs = docs

    if not docs:
        st.session_state.doc_idx = None
        st.session_state.doc_name = None
        st.session_state.page_index = None
        return

    target_idx = 0
    if current_name:
        for i, d in enumerate(docs):
            if d["name"] == current_name:
                target_idx = i
                break

    st.session_state.doc_idx = target_idx
    st.session_state.doc_name = docs[target_idx]["name"]

    page_index = current_page if current_page is not None else 0
    max_page = len(docs[target_idx]["pages"])
    page_index = min(page_index, max_page - 1)
    st.session_state.page_index = max(page_index, 0)
