from collections import Counter
from collections import defaultdict
import math
import re

#Calculates the mutual information scores
def calculate_mutual_information_new(node, collocates, corpus):
    f_node = 0
    f_collocate_counts = defaultdict(int)
    size = 0
    all_mutinfo = []
    for comment in corpus:
        comment = re.sub(r"[^a-zA-Z\s]", " ", comment)
        if node in comment:
            hits = comment.count(node)
            f_node += hits
        for item in collocates:
            if item[1] >= 5:
                f_collocate_counts[item[0]] += comment.count(item[0])
        words = comment.split()
        size += len(words)
    print(f"Corpus word count: {size}, Frequency of Node: {f_node}")
    for item in collocates:
        if item[1] >= 5:
            f_collocate = f_collocate_counts[item[0]]
            f_collocation = item[1]
            numerator = f_collocation * size
            denominator = f_node * f_collocate
            if numerator == 0 or denominator == 0:
                print(f"There is a zero! Collocate: {item[0]}, freq of node: {f_node}, freq of collocate: {f_collocate}, freq of collocation: {f_collocation}, size: {size}")
                continue
            mutinfo = math.log(numerator / denominator, 2)
            all_mutinfo.append([item[0], item[1], mutinfo])
    return all_mutinfo

def count_the_words(utterances):
    #Provides the word counts with different word definitions
    word_counts = []
    word_counts_no_numbers = []
    for utterance in utterances:
        #counts both word counts: first includes e.g. "dog12" and "p_c", the second recognizes words with only letters
        wordlimit1 = re.findall(r"\b\w+\b", utterance)
        word_count = len(wordlimit1)
        wordlimit2 = re.findall(r"\b[a-zA-Z]+\b", utterance)
        word_count_no_numbers = len(wordlimit2)
        word_counts.append(word_count)
        word_counts_no_numbers.append(word_count_no_numbers)
    total_word_count = sum(word_counts)
    total_word_count_no_numbers = sum(word_counts_no_numbers)
    return total_word_count, total_word_count_no_numbers

def collocate_finder(utterances, node):
    node_list = node.split()
    node_length = len(node_list)
    counter = 0
    collocates = []
    concordances = []
    #The file name should be updated for each keyword
    file_path = r"C:\Users\_.txt"
    for text in utterances:
        id = text.split("--")[0].strip()
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        lower_text = text.lower()
        hits = lower_text.count(node)
        if hits > 0:
            counter += hits
            words = lower_text.split()
            for i in range(len(words)):
                if words[i:i+node_length] == node_list:
                    start_idx = max(i - 5, 0)
                    end_idx = min(i + node_length + 5, len(words))
                    before = words[start_idx:i]
                    after = words[i + node_length:end_idx]
                    conc_node = " ".join(node_list)
                    conc_start = " ".join(before)
                    conc_end = " ".join(after)
                    concordance = f"{conc_start} _ {conc_node} _ {conc_end}"
                    colloc = before + after
                    collocates.append(colloc)
                    concordance_and_ID = f"ID: {id}, concordance: {concordance}"
                    concordances.append(concordance_and_ID)
    with open(file_path, "w", encoding="utf-8") as file:
        for line in concordances:
            file.write(f"{line}\n")
    return collocates, concordances

def count_the_collocates(collocates):
    separated = []
    for item in collocates:
        separated.extend(item)
    word_count = Counter(separated)
    unique_words_f = list(word_count.items())
    sorted_list = sorted(unique_words_f, key=lambda x: x[1], reverse=True)
    return sorted_list

def corpus_str(corpus):
    #breaks up the list into a string object
    corpus_text = " ".join(corpus)
    return corpus_text

def keyword_finder(utterances, keyword):
    #not used?
    keyword_positions = []
    for utterance in utterances:
        positions = []
        start = 0
        while True:
            pos = utterance.find(keyword, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + len(keyword)
        keyword_positions.append(positions)
    return keyword_positions

def list_of_concordances(corpus, node):
    concordances = []
    for line in corpus:
        if node in line:
            concordances.append(line)
    return concordances

def count_of_utterances(corpus):
    count = len(corpus)
    word_count = 0
    for line in corpus:
        word_count += len(line)
    return count

#Open the corpus and read all the lines
lines = []
wordcountinitial = 0
file_path = r"C:\Users\corpus.txt" 
with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        line = line.lower()
        lines.append(line)
        line_str = line.split()
        wordcountinitial += len(line_str)
print(f"Initial wordcount without any edits: {wordcountinitial}")

#add the utterances into a list
utterances = []
current_entry = None
pattern = re.compile(r"^\d+ -- \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2};")
for line in lines:
    if pattern.match(line):
        if current_entry is not None:
            utterances.append(current_entry)
        current_entry = line
    else:
        if current_entry is not None:
            current_entry += " " + line
if current_entry is not None:
    utterances.append(current_entry)

#edit the text: remove links, make it lowercase
cleaned_list = []
for text in utterances:
    clean_text = re.sub(r"http\S+|www\S+", "", text)
    clean_text = clean_text.lower()
    cleaned_list.append(clean_text)

#insert the keyword here:
node = ("freedom of expression")

utterances = cleaned_list
edited_count = count_of_utterances(utterances)
print("Utterance count done")
collocates = collocate_finder(utterances, node)
print("Collocates found")
separate = count_the_collocates(collocates[0])
print("Collocates into tuples")
concordance_list = list_of_concordances(utterances, node)
print("Concordance list done")
mutinfo = calculate_mutual_information_new(node, separate, utterances)
print("mutinfo done")
sorted_mutinfo = sorted(mutinfo, key=lambda x: x[2])
file_MI = r"C:\Users\_.txt"
with open(file_MI, "w", encoding="utf-8") as file:
    for info in sorted_mutinfo:
        print(info)
        file.write(f"{info} \n")

print(f"How many utterances: {edited_count}")
