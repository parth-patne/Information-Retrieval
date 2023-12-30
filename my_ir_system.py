import os
import argparse
import string
from collections import defaultdict
from time import time
from time import perf_counter
import re


def load_stopwords(filename):
    with open(filename, 'r') as file:
        stop_words = set(word.strip().lower() for word in file)
    return stop_words

def remove_stopwords_and_punctuations(text, stop_words):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation.replace('\'', '')))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    text = ' '.join(words)
    return text

def split_fables(file_name):
    with open(file_name, 'r') as file:
        content = file.read()
    content = content.split('\n', 306)[-1]
    fables = re.split('\n\n\n\n', content)
    output_folder = 'collection_original'
    output_folder_no_stopwords = 'collection_no_stopwords'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(output_folder_no_stopwords):
        os.makedirs(output_folder_no_stopwords)
    for index, fable in enumerate(fables, start=1):
        lines = fable.strip().split('\n')
        title = lines[0].strip()
        text = '\n'.join(lines[2:]).strip()
        fable_number = str(index).zfill(2)
        fable_name = re.sub(r'[_,\']+', '', title.lower().strip()).replace(' ', '_')
        file_name = "{}_{}.txt".format(fable_number, fable_name)
        with open(os.path.join(output_folder, file_name), 'w') as f:
            f.write(f"{title}\n\n{text}\n\n")
        text = remove_stopwords_and_punctuations(text, stop_words)
        with open(os.path.join(output_folder_no_stopwords, file_name), 'w') as f:
            f.write(f"{title}\n\n{text}\n\n")

def calculate_precision_recall(query, matching_files, relevant_docu):
    relevant_documents = relevant_docu
    matching_ids = []
    for i in matching_files:
        i = int(i[0:2])
        matching_ids.append(i)

    num_retrieved = len(matching_ids)
    num_relevant = len(relevant_documents)

    # Flatten the relevant_documents list
    relevant_documents_flat = [item for sublist in relevant_documents for item in sublist] if any(isinstance(item, list) for item in relevant_documents) else relevant_documents
    
    # Convert lists to sets
    matching_ids_set = set(matching_ids)
    relevant_documents_set = set(relevant_documents_flat)
    
    num_retrieved_relevant = len(matching_ids_set.intersection(relevant_documents_set))

    precision = num_retrieved_relevant / num_retrieved if num_retrieved > 0 else 0
    recall = num_retrieved_relevant / num_relevant if num_relevant > 0 else 0

    return precision, recall

def read_ground_truth_file(file_path):
    ground_truth_terms = {}

    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            try:
                term, ids = line.strip().split(" - ")
                ids = [int(x) for x in ids.split(", ")]
                ground_truth_terms[term] = ids
            except ValueError:
                # Skipping the lines that don't follow the expected format
                continue
    return ground_truth_terms

def linear_search(query, document_type, perform_stemming):
    search_folder = 'collection_original' if document_type == 'original' else 'collection_no_stopwords'
    result_files = []

    

    if '&' in query or '|' in query or query.startswith('!'):
        operator = None
        if '&' in query:
            operator = '&'
        elif '|' in query:
            operator = '|'
        
        if operator:  # Handle conjunction or disjunction
            term1, term2 = query.split(operator)
            if perform_stemming:
                term1, term2 = stem(term1), stem(term2)
            for file_name in os.listdir(search_folder):
                with open(os.path.join(search_folder, file_name), 'r') as file:
                    content = file.read().lower()
                    if perform_stemming:
                        content = stem(content)
                    if (operator == '&' and re.search(r'\b' + term1 + r'\b', content) and re.search(r'\b' + term2 + r'\b', content)) or \
                       (operator == '|' and (re.search(r'\b' + term1 + r'\b', content) or re.search(r'\b' + term2 + r'\b', content))):
                        result_files.append(file_name)
        else:  # Handle negation
            term = query[1:]
            if perform_stemming:
                term = stem(term)
            for file_name in os.listdir(search_folder):
                with open(os.path.join(search_folder, file_name), 'r') as file:
                    content = file.read().lower()
                    if perform_stemming:
                        content = stem(content)
                    if not re.search(r'\b' + term + r'\b', content):
                        result_files.append(file_name)
    else:  # Handle simple search
        if perform_stemming:
            query = stem(query)
        for file_name in os.listdir(search_folder):
            with open(os.path.join(search_folder, file_name), 'r') as file:
                content = file.read().lower()
                if perform_stemming:
                    content = stem(content)
                if re.search(r'\b' + query + r'\b', content):
                    result_files.append(file_name)
    end_time = perf_counter()
    relevant_docu = ground_truth_terms.get(query, [])
    precision,recall = calculate_precision_recall(query, result_files, relevant_docum)
    if precision == 0.000:
        precision = '?'
    else:
        precision = f"{precision:.3f}"

    if recall == 0.000:
        recall = '?'
    else:
        recall = f"{recall:.3f}"

    print('\n'.join(sorted(result_files)))
    print(f"\nT={(end_time - start_time)*1000:.3f}ms P= {precision}, R= {recall}")
 

def create_inverted_index(folder,stemming):
    inverted_index = defaultdict(set)
    for file_name in os.listdir(folder):
        with open(os.path.join(folder, file_name), 'r') as file:
            content = file.read().lower()
            words = content.split()
            for word in words:
                inverted_index[word].add(file_name)
    if stemming:
        inverted_index_stemed = defaultdict(set)
        punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        for i in inverted_index:
            j=i
            for l in punctuations:
                if l in i:
                    i = i.replace(l,"")
            i = i.lower()
            i = stem(i)
            inverted_index_stemed[i].update(inverted_index[j])
            # if "anim" in i:
                # print("i: "+str(i))
                # print("j: "+str(j))
                # print("animal: "+str(inverted_index[j]))
        #print("inverted_index: "+str(inverted_index))
        return inverted_index_stemed
    else:
        return inverted_index

def inverted_index_search(query, inverted_index, perform_stemming=False):

    if query.startswith('!'):
        query = query[1:]
        if perform_stemming:
            query = stem(query)
        result_files = set(os.listdir('collection_no_stopwords')) - inverted_index[query]
    else:
        if '&' in query or '|' in query:
            operator = '&' if '&' in query else '|'
            term1, term2 = query.split(operator)
            if perform_stemming:
                term1, term2 = stem(term1), stem(term2)
            result_files = inverted_index[term1] & inverted_index[term2] if operator == '&' else inverted_index[term1] | inverted_index[term2]
        else:
            if perform_stemming:
                query = stem(query)
            result_files = inverted_index[query]

    end_time = perf_counter()
    #print("ground_truth_terms:", ground_truth_terms)
    #print(query)
    #relevant_docu = ground_truth_terms.get(query, [])
    
    precision,recall = calculate_precision_recall(query, result_files, relevant_docum)
    if precision == 0.000:
        precision = '?'
    else:
        precision = f"{precision:.3f}"

    if recall == 0.000:
        recall = '?'
    else:
        recall = f"{recall:.3f}"

    print('\n'.join(sorted(result_files)))
    print(f"\nT={(end_time - start_time)*1000:.3f}ms P= {precision}, R= {recall}")


def stem(word):
    # Step 1a
    if word.endswith('sses'):
        word = word[:-2]
    elif word.endswith('ies'):
        word = word[:-2]
    elif word.endswith('ss'):
        pass
    elif word.endswith('s'):
        word = word[:-1]

    # Step 1b
    if re.search(r"(.*[aeiouy].*)eed$", word):
        if len(re.findall(r"[aeiouy]", re.search(r"(.*[aeiouy].*)eed$", word).group(1))) > 0:
            word = re.sub(r"eed$", "ee", word)
    elif re.search(r"(.*[aeiouy].*)ed$", word):
        if len(re.findall(r"[aeiouy]", re.search(r"(.*[aeiouy].*)ed$", word).group(1))) > 0:
            word = re.sub(r"ed$", "", word)
            if re.search(r"(.*[aeiouy].*)at$", word):
                word = re.sub(r"at$", "ate", word)
            elif re.search(r"(.*[aeiouy].*)bl$", word):
                word = re.sub(r"bl$", "ble", word)
            elif re.search(r"(.*[aeiouy].*)iz$", word):
                word = re.sub(r"iz$", "ize", word)
            elif re.search(r"(.*[bdglmnprst].*)\1$", word) and not re.search(r"(.*[lsz].*)\1$", word):
                word = word[:-1]
    elif re.search(r"(.*[aeiouy].*)ing$", word):
        if len(re.findall(r"[aeiouy]", re.search(r"(.*[aeiouy].*)ing$", word).group(1))) > 0:
            word = re.sub(r"ing$", "", word)
            if re.search(r"(.*[aeiouy].*)at$", word):
                word = re.sub(r"at$", "ate", word)
            elif re.search(r"(.*[aeiouy].*)bl$", word):
                word = re.sub(r"bl$", "ble", word)
            elif re.search(r"(.*[aeiouy].*)iz$", word):
                word = re.sub(r"iz$", "ize", word)
            elif re.search(r"(.*[bdglmnprst].*)\1$", word) and not re.search(r"(.*[lsz].*)\1$", word):
                word = word[:-1]

    # Step 1c
    if word.endswith('y'):
        if re.search('[aeiou]', word[:-1]):
            word = word[:-1] + 'i'

    # Step 2
    if word.endswith('ational'):
        if re.search('[aeiou]', word[:-7]):
            word = word[:-5]
    elif word.endswith('tional'):
        if re.search('[aeiou]', word[:-6]):
            word = word[:-2]
    elif word.endswith('enci'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-1]
    elif word.endswith('anci'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-1]
    elif word.endswith('izer'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-1]
    elif word.endswith('abli'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-1]
    elif word.endswith('alli'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-2]
    elif word.endswith('entli'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-2]
    elif word.endswith('eli'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-1]
    elif word.endswith('ousli'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-2]
    elif word.endswith('ization'):
        if re.search('[aeiou]', word[:-7]):
            word = word[:-5]
    elif word.endswith('ation'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-3]
    elif word.endswith('ator'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-2]
    elif word.endswith('alism'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-3]
    elif word.endswith('iveness'):
        if re.search('[aeiou]', word[:-7]):
            word = word[:-5]
    elif word.endswith('fulness'):
        if re.search('[aeiou]', word[:-7]):
            word = word[:-4]
    elif word.endswith('ousness'):
        if re.search('[aeiou]', word[:-7]):
            word = word[:-4]
    elif word.endswith('aliti'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-3]
    elif word.endswith('iviti'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-3]
    elif word.endswith('biliti'):
        if re.search('[aeiou]', word[:-6]):
            word = word[:-5]

    # Step 3
    if word.endswith('icate'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-3]
    elif word.endswith('ative'):
        if re.search('[aeiou]', word[:-5]):
            word = word
    elif word.endswith('alize'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-3]
    elif word.endswith('iciti'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-3]
    elif word.endswith('ical'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-2]
    elif word.endswith('ful'):
        if re.search('[aeiou]', word[:-3]):
            word = word
    elif word.endswith('ness'):
        if re.search('[aeiou]', word[:-4]):
            word = word

    # Step 4
    if word.endswith('al'):
        if re.search('[aeiou]', word[:-2]):
            word = word[:-2]
    elif word.endswith('ance'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-4]
    elif word.endswith('ence'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-4]
    elif word.endswith('er'):
        if re.search('[aeiou]', word[:-2]):
            word = word[:-2]
    elif word.endswith('ic'):
        if re.search('[aeiou]', word[:-2]):
            word = word[:-2]
    elif word.endswith('able'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-4]
    elif word.endswith('ible'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-4]
    elif word.endswith('ant'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]
    elif word.endswith('ement'):
        if re.search('[aeiou]', word[:-5]):
            word = word[:-5]
    elif word.endswith('ment'):
        if re.search('[aeiou]', word[:-4]):
            word = word[:-4]
    elif word.endswith('ent'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]
    elif word.endswith('ion'):
        if re.search('[aeiou]', word[:-3]):
            if re.search('[st]$', word[:-3]):
                word = word[:-3]
    elif word.endswith('ou'):
        if re.search('[aeiou]', word[:-2]):
            word = word[:-2]
    elif word.endswith('ism'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]
    elif word.endswith('ate'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]
    elif word.endswith('iti'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]
    elif word.endswith('ous'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]
    elif word.endswith('ive'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]
    elif word.endswith('ize'):
        if re.search('[aeiou]', word[:-3]):
            word = word[:-3]

    # Step 5a
    if word.endswith('e'):
        if len(word) > 1:
            word = word[:-1]
        elif len(word) == 1:
            if not re.search('[aeiou]', word):
                word = word[:-1]

    # Step 5b
    if word.endswith('ll') and re.search('[aeiou]', word[:-2]):
        word = word[:-1]

    return word


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A basic information retrieval system.")
    parser.add_argument('--extract-collection', type=str, help="Path to the 'fables' file to extract the collection")
    parser.add_argument('--remove-stopwords', action='store_true', help="Remove stop words from the collection")
    parser.add_argument('--query', type=str, help="The query to search")
    parser.add_argument('--model', type=str, choices=['bool', 'vect'], help="The search model to use")
    parser.add_argument('--documents', type=str, choices=['original', 'no_stopwords'], help="The type of documents to search in")
    parser.add_argument('--stemming', action='store_true', help="Perform stemming on the query and the documents")
    parser.add_argument('--search-mode', type=str, choices=['linear', 'inverted'], help="The type of search to perform")
    args = parser.parse_args()
    start_time = perf_counter()
    stop_words = load_stopwords('englishST.txt')
    global ground_truth_terms
    ground_truth_terms = read_ground_truth_file('ground_truth.txt')
    relevant_docum = ground_truth_terms.get(args.query, [])
    if args.extract_collection:
        split_fables(args.extract_collection)

    if args.remove_stopwords:
        remove_stopwords()

    if args.query and args.model == 'bool':
        if args.stemming:
            stemmed_query = stem(args.query)
            print("Stemmed Query:", stemmed_query)
        else:
            stemmed_query = args.query

        if args.search_mode == 'linear':
            linear_search(stemmed_query, args.documents, args.stemming)
        elif args.search_mode == 'inverted':
            inverted_index = create_inverted_index('collection_no_stopwords' if args.documents == 'no_stopwords' else 'collection_original', args.stemming)
            inverted_index_search(stemmed_query, inverted_index, args.stemming)
