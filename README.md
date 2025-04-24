# Information Retrieval System

A simple information retrieval system implemented in Python. It allows you to extract a collection of fables, clean the text, and perform search queries using Boolean and Vector space models.

---

## Features

- **Collection Extraction**: Extract a collection of fables from a specified text file.
- **Stopword Removal**: Remove common stopwords from the documents.
- **Boolean Model**: Search using Boolean logic (AND, OR, NOT).
- **Vector Model**: Search using vector space model (cosine similarity).
- **Stemming**: Apply Porter stemming algorithm to queries and documents.
- **Search Modes**: Choose between linear search and inverted index search.
- **Search on Cleaned or Original Documents**: Choose to search on original or stopword-removed documents.
- **Precision and Recall**: Calculate precision and recall for search results.

---

## Usage

1. **Download** the code and navigate to the directory.

2. **Extract the collection** from a file (e.g., Aesop's fables):

   ```bash
   python my_ir_system.py --extract-collection aesopa10.txt
   ```

---

## Searching Options

Use the following command-line arguments to perform different types of searches:

### Boolean Model (with original documents):

```bash
python my_ir_system.py --model bool --search-mode linear --documents original --query "fox&wolf"
```

### Boolean Model (inverted index with stopword removal):

```bash
python my_ir_system.py --model bool --search-mode inverted --documents no_stopwords --query "fox|wolf"
```

### Boolean with Stemming:

```bash
python my_ir_system.py --model bool --search-mode linear --documents original --stemming --query "running&fast"
```

### Vector Model:

```bash
python my_ir_system.py --model vector --documents no_stopwords --query "clever fox"
```

---

## Query Syntax (Boolean Search)

- **AND**: `term1&term2` (e.g., `fox&wolf`)
- **OR**: `term1|term2` (e.g., `fox|wolf`)
- **NOT**: `!term1` (e.g., `!fox`)

---

## Stemming

Uses the **Porter Stemming Algorithm** to normalize words. Enable it using:

```bash
--stemming
```

This applies to both queries and documents.

---

## Search Modes

- **Linear Search**:
  ```bash
  --search-mode linear
  ```

- **Inverted Index Search**:
  ```bash
  --search-mode inverted
  ```

Inverted index search significantly improves efficiency.

---

## Output

- Displays matched documents.
- Shows query processing time in milliseconds, e.g., `T=15ms`.

