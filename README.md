# About
[![Streamlit][streamlit-shield]][streamlit-url] &thinsp;
[![PyMuPDF][pymupdf-shield]][pymupdf-url]

Interactive Streamlit app for inspecting PyMuPDF text extraction results. Upload PDFs, toggle extraction flags, and visualize resulting bounding boxes for blocks, lines, spans, and words overlaid on each page.

<sub>*For details on page structure, see [PyMuPDF's official docs](https://pymupdf.readthedocs.io/en/latest/).*</sub>

# Getting started

A short, practical guide on how to use and customize the app. 

## Use The Deployed App

* Follow this link: [https://pdf-inspector.streamlit.app/]

  This is the fastest way to see the app working without installing anything.

  If the deployed link fails, follow the instructions below to run the app locally. 

## Run Locally

### Get the code

Below are three quick ways to obtain the project source before you run the app locally.

#### 1) Clone (recommended)

Clone the official repository with SSH or HTTPS.

```bash
# SSH
git clone git@github.com:<owner>/<repo>.git
cd <repo>

# or HTTPS
git clone https://github.com/<owner>/<repo>.git
cd <repo>
```

#### 2) Fork (for contributors)

Fork the repository on GitHub, then clone your fork locally to make changes and push branches.

```bash
# after forking on GitHub
git clone git@github.com:<your-github-username>/<repo>.git
cd <repo>

# create a feature branch
git checkout -b feature/describe-change
```

#### 3) Download

If you do not want to use Git, download the repository as a ZIP from GitHub (Code → Download ZIP), unzip the archive, and open the extracted folder.

### Set up the project environment 

1. Ensure you have:

   * Python (see `.python-version` for the target interpreter)
   * pip

2. Create and activate a virtual environment (recommended)

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

### Launch the app

From the root of the project directory, run this one line

```bash
streamlit run app.py
```

Notes

* The app will open in your default browser. The first launch may take longer than normal.  
* To run on a different port: `streamlit run app.py --server.port {####}`.

## Usage
- Upload one or more PDFs in the sidebar; uploads are sorted by name.
- Use the document and page selectors to step through files.
- Choose a level (`blocks`, `lines`, `spans`, `words`) to highlight.
- Adjust DPI to change raster quality; changes re-render all pages (note: for multi-file uploads, this can take a long time for high DPI; infrequent changes recommended).
- Switch OCR mode (`off`, `auto`, `full`) and toggle PyMuPDF text flags to see how extraction affects bounding boxes at each level.
- Scroll or drag on the Plotly view to zoom and pan around the page.

[streamlit-shield]: https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white
[streamlit-url]: https://github.com/streamlit/streamlit

[pymupdf-shield]: https://img.shields.io/badge/PyMuPDF-007AFF?style=flat&logo=python&logoColor=white
[pymupdf-url]: https://github.com/pymupdf/PyMuPDF
