from statistics import mean, median, mode, StatisticsError
import datetime
import re
import json
import os
from collections import Counter

#Combines the filepath
def input_path_initializer(base_path, *subfolder, file):
    return os.path.join(base_path, *subfolder, file)

#Combines the output filepath
def output_path_initiliazer(base_path, *subfolder, output_file):
    return os.path.join(base_path, *subfolder, output_file)

#Takes the individual files of each subreddit and combines them into one file
def combine_files(file_paths, output_file):
    with open(output_file, "w", encoding='utf-8') as output_file:
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as input_file:
                    content = input_file.read()
                    output_file.write(content + '\n')
                print(f"Successfully added contents of {file_path}.")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

#For downloading the data from the ConvoKit utterances-file for the first time, adds the metadata
def download_the_data(file_path, output_file_path):
    #Change the ID when downloading more than one file in order to allow the differentiation of the subreddits based on this
    ID = 0
    print("downloading the data")
    utterances = []
    with open(file_path, 'r', encoding="utf-8") as file:
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            for line in file:
                data = json.loads(line)
                timestamp = data["timestamp"]
                date = datetime.datetime.utcfromtimestamp(timestamp)
                text = str(data.get("text", ""))
                #Remove empty utterances and add the metadata and data to a new file
                if text.strip() and text.strip() != "[deleted]" and text.strip() != "[removed]":
                    output_file.write(f"{ID} -- {date}; {text}\n")
                    line_info = f"{ID} -- {date}; {text}\n"
                    line_info = line_info.lower()
                    utterances.append(line_info)
                    ID = ID + 1
    print("data download done")
    return utterances

#After the data has been downloaded and metadata added
def download_corpus(output_file_path):
    lines = []
    with open(output_file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.lower()
            lines.append(line)
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
    return utterances

#Counts the occurrences of the keywords and number of utterances
def keyword_counter(utterances, keyword1, keyword2, keyword3):
    utterance_count = 0
    keyword_count = 0
    keyword1_count = 0
    keyword2_count = 0
    keyword3_count = 0
    for line in utterances:
        utterance_count += 1
        keyword1_occurrences = line.count(keyword1)
        keyword2_occurrences = line.count(keyword2)
        keyword3_occurrences = line.count(keyword3)
        keyword1_count += keyword1_occurrences
        keyword2_count += keyword2_occurrences
        keyword3_count += keyword3_occurrences
        keyword_count += keyword1_occurrences + keyword2_occurrences + keyword3_occurrences
    print(f"Utterances: {utterance_count}, {keyword1} = {keyword1_count}, {keyword2} = {keyword2_count}, {keyword3} = {keyword3_count}, keyword total = {keyword_count}")

#Makes the utterances into a string object for the date analysis
def utterances_to_strings(utterances):
    corpus_text = " ".join(utterances)
    return corpus_text

def find_dates(text):
    pattern = r"-- (\d{4}-\d{2}-\d{2})"
    dates = re.findall(pattern, text)
    return dates

def newest_oldest_finder(dates):
    formatted_dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates]
    sorted_dates = sorted(formatted_dates)
    newest_date = sorted_dates[-1]
    oldest_date = sorted_dates[0]
    return newest_date, oldest_date

def word_count_statistics(utterances):
    #Calculate the word count with metadata, links, numbers and punctuation)
    wordcountinitial = 0
    for line in utterances:
        line_str = line.split()
        wordcountinitial += len(line_str)
    print(f"This is the initial word count with links, numbers, punctuation and metadata: {wordcountinitial}")
    #Calculate the word count without metadata. Metadata is 4 words per utterance
    no_metadata_counts = []
    word_count_no_metadata = 0
    for line in utterances:
        if ";" in line:
            no_metadata = line.split(";", 1)[1]
            line_str = no_metadata.split()
            word_count_no_metadata += len(line_str)
            no_metadata_counts.append(len(line_str))
        else:
            print(f"There is an issue with this line: {line}")
    print(f"Wordcount without metadata, no other edits: {word_count_no_metadata}")
    #Filter links from the utterances
    filtered_data = []
    url_regex = re.compile(r"(https?://\S+|www\.\S+)")
    filtered_data = [url_regex.sub("", item) for item in utterances]
    wordcountnolinks = 0
    for line in filtered_data:
        line_str = line.split()
        wordcountnolinks += len(line_str)
    print(f"This is the word count without links: {wordcountnolinks}")
    #Filter numbers and punctuation from the utterances
    numpunc_regex = re.compile(r"\b[a-zA-Z]+\b")
    onlyletters = [numpunc_regex.sub(' ', item) for item in filtered_data]
    wordcountnonumpunc = 0
    for line in onlyletters:
        line_str = line.split()
        wordcountnonumpunc += len(line_str)
    print(f"This is the word count without numbers or punctuation (can't shows up as two words): {wordcountnonumpunc}")
    meanwc = mean(no_metadata_counts)
    medianwc = median(no_metadata_counts)
    try:
        modewc = mode(no_metadata_counts)
    except StatisticsError:
        modewc = None
    print(f"Mean: {meanwc}, median: {medianwc} and mode: {modewc}, these include links, numbers and punctuation, but excludes metadata")
    #Return the data without the links
    return filtered_data

#Initialize the file paths
base_path = r"C:\Users\Käyttäjä\.convokit\downloads"
subfolder = "subreddit-AskAnAmerican"
file = "utterances.jsonl"
output_subfolder = "final_files"
output_file = "All.txt"

#These can be run everytime, but input_path_initializer only needed for the initial downloading
full_path = input_path_initializer(base_path, subfolder, file=file)
output_full_path = output_path_initiliazer(base_path, output_subfolder, output_file=output_file)
print("Path created")

#Run download_the_data only when downloading data, otherwise use download_corpus
#utterances = download_the_data(full_path, output_full_path)
utterances = download_corpus(output_full_path)
print("Corpus downloaded")

utterances = word_count_statistics(utterances)
print("Utterance statistics done")

#Counts utterances and keyword occurrances
keyword1 = "free speech"
keyword2 = "freedom of speech"
keyword3 = "freedom of expression"
keywords = (keyword1, keyword2, keyword3)
keyword_count = keyword_counter(utterances, *keywords)
print("Keywords and utterances counted")

#Makes the corpus into a string object, might not work with the compiled file, but only needed for dates
#corpus_text = utterances_to_strings(utterances)
#print("Turned into a string")

#Provides the earliest and latest dates, can be used each time but might not work with the compiled file
#dates = find_dates(corpus_text)
#newest_date, oldest_date = newest_oldest_finder(dates)
#print("Newest date:", newest_date.strftime('%Y-%m-%d'))
#print("Oldest date:", oldest_date.strftime('%Y-%m-%d'))

#For combining files, remember to edit the output_file_path aswell
file_paths = [r"C:\Users\Käyttäjä\.convokit\downloads\final_files\USHistory.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\scotus.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\usanews.txt",  
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\AmericanPolitics.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\uscg.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\usa.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\uspolitics.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\ussoccer.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\USMC.txt", 
              r"C:\Users\Käyttäjä\.convokit\downloads\final_files\AskAnAmerican.txt"]
#For combining the files of individual subreddits into one file
#combine_files(file_paths, output_full_path)

print("Ready")
