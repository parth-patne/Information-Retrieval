## Information Retirval System

This is a basic information retrieval system implemented in Python. The system allows you to extract a collection of fables, remove stopwords, and perform search queries using different search models and techniques.

## Features

Collection Extraction: Extract the collection of fables from a specified file.
Stopword Removal: Remove stopwords from the collection.
Boolean Model: Perform search queries using the Boolean model.
Vector Model: Perform search queries using the Vector model.
Original Documents: Search within the original documents.
Documents without Stopwords: Search within the documents without stopwords.
Stemming: Perform stemming on the query and the documents.
Linear Search: Perform a linear search using the specified search mode.
Inverted Index Search: Perform an inverted index search using the specified search mode.
Precision and Recall Calculation: Calculate precision and recall values for the search results.

## Usage
To use the information retrieval system, follow these steps:

1.Download the code and save it to a directory of your choice.

2.Prepare the collection of fables by providing the path to the "fables" file. Use the --extract-collection command-line argument followed by the file path. For example:

python my_ir_system.py --extract-collection aesopa10.txt

## Stemming
The information retrieval system implements the Porter stemming algorithm for word stemming. The algorithm follows the rules specified in the "porter.txt" file, which provides a comprehensive description of the algorithm.

To enable stemming, use the --stemming command-line argument. When specified, the system will perform stemming on both the query and the documents, allowing you to search using stemmed terms.

For example:

python my_ir_system.py --model "bool" --search-mode "linear" --documents "original" --stemming --query "somesearchterm"

This command performs a Boolean model search using stemmed terms in the original documents.

## Inverted List for Boolean Retrieval
The information retrieval system provides an inverted list as an alternative to linear search for Boolean retrieval. The inverted list improves search efficiency by using an index structure.

To use the inverted list, set the --search-mode command-line argument to "inverted". This enables the system to utilize the inverted list for Boolean search operations.

You can perform conjunction, disjunction, and negation operations using the following syntax in your query:

Conjunction: t1&t2 (e.g., fox&wolf)
Disjunction: t1|t2 (e.g., fox|wolf)
Negation: -t1 (e.g., !fox)
For example:

python my_ir_system.py --model "bool" --search-mode "inverted" --documents "original" --query "somesearchterm"

This command performs an inverted list search using the conjunction of terms "fox" and "wolf" in the original documents.

The system will measure the time taken for query processing and display it in milliseconds at the end of the results list in the format "T=<value>ms".

## Searching

Once the collection is prepared, you can perform search queries using the information retrieval system. Here are the available search options:

Boolean Model: Use the --model bool command-line argument to enable the Boolean model.

Original Documents: Use the --documents original command-line argument to search in the original documents.

Documents without Stopwords: Use the --documents no_stopwords command-line argument to search in the documents without stopwords.

Stemming: Use the --stemming command-line argument to enable stemming for both the query and the documents.

Linear Search: Use the --search-mode linear command-line argument to perform a linear search.

Inverted Index Search: Use the --search-mode inverted command-line argument to perform an inverted index search.
