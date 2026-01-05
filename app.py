import streamlit as st
import handlers

# app configuration
st.set_page_config(layout="wide")
handlers.init_helper_states()
handlers.reconcile_docs()


# app sidebar
with st.sidebar:

    # pdf upload expander
    with st.container(key="upload_container", gap=None, height="content"):
        st.file_uploader(
            key="uploads",
            label="Upload Documents",
            type="pdf",
            accept_multiple_files=True,
            label_visibility="collapsed",
            width="stretch",
            on_change=handlers.on_upload,
        )
        
    with st.container(key="nav_container", gap=None):

        with st.container(key="doc_nav", gap=None):

            # doc selector
            st.selectbox(
                label="PDF",
                options=handlers.doc_names(),
                key="doc_name",
                on_change=handlers.on_doc_change,
                placeholder="Upload folder empty."
            )

            # nav buttons for prev/next doct 
            with st.container(horizontal=True, horizontal_alignment="distribute", gap=None):

                st.button(
                    key="doc_prev",
                    label="<-",
                    type="tertiary",
                    disabled=handlers.doc_prev_disabled(),
                    on_click=handlers.on_doc_prev,
                )

                st.button(
                    key="doc_next",
                    label="->",
                    type="tertiary",
                    disabled=handlers.doc_next_disabled(),
                    on_click=handlers.on_doc_next,
                )

        # page navigation container
        with st.container(key='page_nav', gap=None):
            
            st.selectbox(
                key='page_index',
                label='PAGE',
                options=handlers.page_indices(),
                placeholder="Upload folder empty.",
            )
            
            with st.container(horizontal=True, horizontal_alignment="distribute", gap=None):

                st.button(
                    key="page_prev",
                    label="<-",
                    type="tertiary",
                    disabled=handlers.page_prev_disabled(),
                    on_click=handlers.on_page_prev,
                )

                st.button(
                    key="page_next",
                    label="->",
                    type="tertiary",
                    disabled=handlers.page_next_disabled(),
                    on_click=handlers.on_page_next,
                )
        
        # highlight-level navigation container
        with st.container(key='level_nav', gap=None):
            
            st.selectbox(
                key='level_select',
                label='LEVEL',
                options=handlers.LEVELS
            )
            
            with st.container(horizontal=True, horizontal_alignment="distribute", gap=None):

                st.button(
                    key='level_prev',
                    label='<-',
                    type='tertiary',
                    disabled=handlers.level_prev_disabled(),
                    on_click=handlers.on_level_prev,
                )

                st.button(
                    key='level_next',
                    label='->',
                    type='tertiary',
                    disabled=handlers.level_next_disabled(),
                    on_click=handlers.on_level_next,
                )

    # PyMuPDF settings container
    with st.container(key='settings_container', gap=None):

        with st.expander(label='RENDER SETTINGS', expanded=False):
            st.slider(
                key='dpi',
                label='DPI',
                min_value=72,
                max_value=600,
                value=450,
                step=10,
                on_change=handlers.on_dpi_change,
                help='Controls page rasterization and box rendering scale.',
            )
        
        # ocr settings expander
        with st.expander(label='OCR SETTINGS', expanded=False):
            st.radio(
                key='ocr_mode',
                label='Mode',
                options=['off','auto','full'],
            )

        # extraction settings expander
        with st.expander(label='EXTRACTION SETTINGS', expanded=False):
            st.checkbox(
                key='text_preserve_ligatures',
                label='TEXT_PRESERVE_LIGATURES',
                value=True,
                help='Keep ligatures (e.g. ffi, fl) as a single glyph instead of expanding.',
            )

            st.checkbox(
                key='text_preserve_whitespace',
                label='TEXT_PRESERVE_WHITESPACE',
                value=True,
                help='Preserve original whitespace instead of normalizing spacing.',
            )

            st.checkbox(
                key='text_preserve_images',
                label='TEXT_PRESERVE_IMAGES',
                value=True,
                help='Include images in text extraction outputs (metadata only for blocks).',
            )

            st.checkbox(
                key='text_inhibit_spaces',
                label='TEXT_INHIBIT_SPACES',
                value=False,
                help='Do not infer missing spaces between characters.',
            )

            st.checkbox(
                key='text_dehyphenate',
                label='TEXT_DEHYPHENATE',
                value=False,
                help='Remove line-end hyphens and join words across lines.',
            )

            st.checkbox(
                key='text_preserve_spans',
                label='TEXT_PRESERVE_SPANS',
                value=False,
                help='Force one span per line in structured outputs.',
            )

            st.checkbox(
                key='text_mediabox_clip',
                label='TEXT_MEDIABOX_CLIP',
                value=True,
                help='Ignore characters outside the page mediabox.',
            )

            st.checkbox(
                key='text_use_cid_for_unknown_unicode',
                label='TEXT_USE_CID_FOR_UNKNOWN_UNICODE',
                value=True,
                help='Use raw character codes for unknown glyphs.',
            )

            st.checkbox(
                key='text_accurate_bboxes',
                label='TEXT_ACCURATE_BBOXES',
                value=False,
                help='Compute bounding boxes from glyph outlines instead of font metrics.',
            )

            st.checkbox(
                key='text_ignore_actualtext',
                label='TEXT_IGNORE_ACTUALTEXT',
                value=False,
                help='Ignore embedded replacement text in favor of rendered text.',
            )

            st.checkbox(
                key='text_segment',
                label='TEXT_SEGMENT',
                value=False,
                help='Attempt to segment page into different regions.',
            )

# main panel
with st.container(key='main_panel',gap=None):
    
    fig = handlers.current_page_figure(
        handlers.current_flags(),
        handlers.current_ocr_mode(),
        handlers.current_dpi(),
    )

    if fig:
        st.plotly_chart(
            fig,
            width="content",
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": ["pan2d", "autoScale2d"],
                "scrollZoom": True,
                "responsive": False,
            },
        )
