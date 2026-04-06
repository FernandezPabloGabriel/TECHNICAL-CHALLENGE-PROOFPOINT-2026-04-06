# Take into consideration the following cases:
# 1. Words separated by a hyphen are considered as one. E.g. "decision-making"
# 2. Words written with or without accent depending on the context are considered different words. E.g. "café" and "cafe" are 2 different words
# 3. 's, 't, 're, 've, 'm, 'll are considered as individual words. E.g. "it's" is considered as "it" and "is"
# 4. Numbers are considered as words. E.g. "2021" is considered as a word.
from operator import itemgetter

def generate_analysis_report(report_path: str, wordsDict: dict):
    mostFrequentWords = count_ten_most_frequent_words(wordsDict)
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write("## Top 10 Most Frequent Words\n")
        for i in range(len(mostFrequentWords)):
            report_file.write(f"{i+1}. **{mostFrequentWords[i][0]}**: `{mostFrequentWords[i][1]}`\n")


def clean_words_and_characters(word: str) -> list:
    # A more aggesive way to compare case insensitive words
    clean_word1 = word.casefold()
    # Transform "’ into "'"
    clean_word2 = clean_word1.replace("’", "'")

    # I could have used regex but decided to do it manually to have more control over the process
    # This list will contain the original line but with all strange characters removed and replaced by a space
    final_clean_word = []

    for i in range(len(clean_word2)):
        char = clean_word2[i]
        prevChar = (i > 0 and clean_word2[i-1].isalnum())
        nextChar = (i + 1 < len(clean_word2) and clean_word2[i+1].isalnum())
        nextCharDigit = (i + 1 < len(clean_word2) and clean_word2[i+1].isdigit()) # In case there is a negative number we consider it a word too
        # Removes strange characters
        if char.isalnum():
            final_clean_word.append(char)
            continue
        elif char == "-" or char == "'":
            if (prevChar and nextChar) or (nextCharDigit and char == "-"):
                final_clean_word.append(char)
                continue
        final_clean_word.append(" ")

    return "".join(final_clean_word).split()


def identify_abbreviations(word: str) -> list:
    if "'re" in word or "'s" in word or "'t" in word or "'ve" in word or "'m" in word or "'ll" in word or "'ld" in word:
        split_word = word.split("'")
        if len(split_word) == 2 and split_word[0] != "":
            if split_word[1] == "re":
                return [split_word[0], "are"]
            elif split_word[1] == "s":
                return [split_word[0], "is"]
            elif split_word[1] == "t":
                return [split_word[0], "not"]
            elif split_word[1] == "ve":
                return [split_word[0], "have"]
            elif split_word[1] == "m":
                return [split_word[0], "am"]
            elif split_word[1] == "ld":
                return [split_word[0], "would"]
            else:
                return [split_word[0], "will"]
    return [word]


def count_words(word, wordsDict):
    if word not in wordsDict:
        wordsDict[word] = 1
    else:
        wordsDict[word] += 1


def extract_words_from_text(wordList: list, wordsDict: dict):
    for word in wordList:
        if word != "":
            if "'" in word:
                abbreviations = identify_abbreviations(word)
                for abbreviation in abbreviations:
                    count_words(abbreviation, wordsDict)
                continue
            count_words(word, wordsDict)


def count_ten_most_frequent_words(wordsDict: dict) -> list:
    sorted_words = sorted(wordsDict.items(), key=itemgetter(1), reverse=True)
    return sorted_words[:10]


def read_txt_file(txt_file_path: str) -> dict | str:
    try:
        with open(txt_file_path, "r", encoding="utf-8") as file:
            wordsDict = {}
            for line in file:
                lineStrip = line.strip()
                if lineStrip == "":
                    continue
                wordList = clean_words_and_characters(lineStrip) # We remove leading and trailing whitespace
                extract_words_from_text(wordList, wordsDict)
            return wordsDict

    except FileNotFoundError:
        return f"File not found: {txt_file_path}"


def main():
    txt_file_path = "words.txt"
    wordsDict = read_txt_file(txt_file_path)
    if isinstance(wordsDict, dict):
        generate_analysis_report("report.md", wordsDict)
        print("Report generated successfully: report.md")
    else:
        print(wordsDict)


if "__main__" == __name__:
    main()