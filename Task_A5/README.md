# Task A5 - Design an AI Application for Citizen Complaints

Measurement script: `python a5_naive_bayes.py` (output_a5_naive_bayes.txt; uses the 50 complaints of Task_B4). The scorer and summariser are implemented in Task_B4.

## A5.1 Sentiment scorer and summariser
Sentiment (lexicon based): two word sets POSITIVE and NEGATIVE and a set NEGATORS (`not, never, no`). Each word gives +1, -1 or 0; if the word before it is a negator the sign is flipped ("not good" = -1, "not bad" = +1). The sum decides the label: above 0 positive, below 0 negative, 0 neutral.
```
BEGIN score(text)
  words = lowercase(text) with punctuation removed, split into words
  total = 0
  FOR i = 0 TO number of words - 1
    value = +1 IF words[i] is in POSITIVE, -1 IF in NEGATIVE, otherwise 0
    IF value is not 0 AND i > 0 AND words[i-1] is in NEGATORS THEN value = -value
    total = total + value
  RETURN total
END
```
Extractive summariser: split into sentences, remove stop words, count how often each important word occurs, give each sentence the sum of the counts of its important words, and return the k best sentences in their original order.
```
BEGIN summarise(text, k)
  sentences = split text at . ! ?
  freq = count of every important word (not a stop word, longer than 2 letters)
  FOR EACH sentence: score = sum of freq[w] for its important words
  best = the k sentences with the highest score
  RETURN best in the order they appear in the text
END
```

## A5.2 Rule-based chatbot
Keyword rules, then a database query:
```
BEGIN reply(question)
  q = lowercase(question)
  station = a station name from the stations table that occurs in q, else none
  IF q contains "pm2.5" OR "pm 2.5" THEN pollutant = pm25  (similarly "pm10", "no")
  IF q contains "today" THEN day = today's date  ELSE IF q contains "yesterday" THEN day = yesterday
  IF station AND pollutant AND day exist THEN
    value = SELECT AVG(pollutant) FROM readings WHERE station = ? AND day = ?    (with ? placeholders)
    IF value exists THEN RETURN "The average PM2.5 in <station> on <day> is <value> ug/m3"
    ELSE RETURN "No readings for <station> on <day> yet"
  ELSE RETURN "Please ask like: What is the PM2.5 in Adyar today?"
END
```
Limitations: it only understands the fixed keywords and station names, so "How bad is the air where I live?" fails; spelling mistakes (`Adayar`) are not matched; it has no memory of the earlier question ("and in Guindy?"); it cannot handle two stations or a time range in one question; it does not understand negation or sarcasm; it knows only the data in the database (an old or missing day gives no answer); and it never explains health advice or the reason for a value.

## Alternative concept: a trained Naive Bayes classifier instead of a word list
Solution: count the words of each class in labelled complaints, then choose the class with the highest `log P(class) + sum of log P(word | class)` (Laplace smoothing). I wrote it in pure Python (`a5_naive_bayes.py`) and tested it by leave-one-out on the 50 complaints with my own labels.

| | Word list (base) | Word list (extended) | Naive Bayes (trained) |
|---|---|---|---|
| Correct labels out of 50 | 37 | 45 (words chosen after seeing the same 50, so optimistic) | 23 (leave-one-out) |
| Time per complaint | 0.0018 ms (extended list) | | 0.0109 ms (about 6 times slower) |
| Memory of the model | 3.1 KB (44 words) | | 30.2 KB (214-word vocabulary) |

Always guessing "negative" gives 25 of 50, so with only 50 training examples the trained model is no better than guessing: it needs thousands of labelled complaints, and a pre-trained language model would need megabytes to gigabytes of memory and milliseconds per complaint, but it can understand context, sarcasm and mixed opinions. Time per complaint is O(words) for both, and the space is O(vocabulary x classes) for Naive Bayes against O(list size) for the word list. Accuracy of a trained model is expected to be higher only when enough labelled data exists.
