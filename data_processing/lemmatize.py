import json
from nltk import pos_tag
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer


def get_wordnet_pos(treebank_tag):
    """Map treebank tags to wordnet tags.

    From https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    """

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # Default to noun when unknown POS is found.


def generate_tokens(review, do_pos=True):
    """Yields a nested list indexed by [sentence, word] populated either by words, or (word, pos) tuples."""
    sent_tokens = sent_tokenize(review)
    result = []
    for sentence in sent_tokens:
        word_tokens = word_tokenize(sentence)
        word_tokens = [word.lower() for word in word_tokens]
        if do_pos:
            word_tokens = pos_tag(word_tokens, tagset='universal')
            word_tokens = [(word, get_wordnet_pos(tag)) for word, tag in word_tokens]
        result.append(word_tokens)

    return result


def lemmatize_word(word, pos):
    """Lemmatize a single word."""
    return lemmatize_word.lemmatizer(word, pos)
lemmatize_word.lemmatizer=WordNetLemmatizer().lemmatize


def lemmatize_tokens(review):
    """Lemmatize a review's tokens. Review should be POS tagged.

    Args:
        review: A nested list of depth 2 with indexing [sentence, word_loc]. Each element is a tuple of (word, pos_tag).

    Returns:
        A nested list of depth 2 with indexing [sentence, word_loc]. Each element is a lemmatized word.
    """
    return [[lemmatize_word(*i) for i in sentence] for sentence in review]


def remove_stopwords(review):
    """Remove stopwords and non-alphanumeric characters from the review."""
    return [[word for word in sentence if (word.isalnum() and word not in remove_stopwords.s_words)]
            for sentence in review]
remove_stopwords.s_words = set(stopwords.words('english'))


def clean_review(review):
    """Cleans a review by tokenizing it, lemmatizing it, and removing stopwords and non alpha-numeric characters."""
    tokens = generate_tokens(review)
    lemmatized = lemmatize_tokens(tokens)
    return remove_stopwords(lemmatized)


with open('data/review.json', 'r') as f:
    reviews = (json.loads(line) for line in f)
    lemmatized = (clean_review(review['text']) for review in reviews)
    print(next(lemmatized))


