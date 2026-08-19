# Book_Tax_Differences
Book-Tax Differences calculator for general educational purposes.

## Setup

1. Create and activate a virtual environment:
   ```
   python3 -m venv myvenv
   source myvenv/bin/activate   # on Windows: myvenv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running locally

### Console version
```
python3 src/app.py
```

### Web version (Streamlit)
```
streamlit run src/streamlit_app.py
```
This opens automatically in your browser at http://localhost:8501.

## Running tests
```
python3 tests/test.py
```
