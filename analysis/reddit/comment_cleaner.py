import nltk
nltk.download("stopwords")
nltk.download("wordnet")
from nltk.corpus import stopwords
from abc import ABC, abstractmethod
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import ahocorasick
from math import nan

tickers = {0: "TSLA",
           1: "MSFT"}

NO_TICKER_ID = "NO_TICKER"


class TickerSearch:
    def __init__(self):
        self.automaton = None

    def configure(self, ticker_dict):
        self.automaton = ahocorasick.Automaton()
        for ticker_index in tickers.keys():
            self.automaton.add_word(ticker_dict[ticker_index], ticker_index)
        self.automaton.make_automaton()

    def search(self, messy_text_body):
        tickers_in_text = [tickers[ticker_index] for (_, ticker_index) in self.automaton.iter(messy_text_body)]
        if not tickers_in_text:
            return NO_TICKER_ID
        return tickers_in_text


class TextCleaner:
    def __init__(self):
        self.stopwords = None
        self.tokeniser = None
        self.lemmatiser = None

    def configure(self, tokeniser=None, lemmatiser=None):
        self.stopwords = stopwords.words('english')
        if tokeniser is None:
            # Removes punctuation as well as tokenising
            self.tokeniser = RegexpTokenizer(r'\w+')
        else:
            self.tokeniser = tokeniser

        if lemmatiser is None:
            self.lemmatiser = WordNetLemmatizer()
            # converts all words to one form of similar meaning i.e. rocks -> rock, better -> good
        else:
            self.lemmatiser = lemmatiser

    def clean(self, text):
        return " ".join([self.lemmatiser.lemmatize(token.lower()) for token in self._tokenise(text) if token.lower()
                         not in self.stopwords])

    def _tokenise(self, text):
        return self.tokeniser.tokenize(text)


class ScoreExtractor(ABC):
    @abstractmethod
    def __call__(self, score_dict):
        pass

    def configure(self, **kwargs):
        pass


class DiracScore(ScoreExtractor):
    def __call__(self, score_dict):
        return score_dict


class CompoundScore(ScoreExtractor):
    def __call__(self, score_dict):
        return score_dict["compound"]


class PositiveScore(ScoreExtractor):
    def __call__(self, score_dict):
        return score_dict["pos"]


class NegativeScore(ScoreExtractor):
    def __call__(self, score_dict):
        return score_dict["neg"]


class NeutralScore(ScoreExtractor):
    def __call__(self, score_dict):
        return score_dict["neu"]


class WeightedScore(ScoreExtractor):
    def configure(self, **kwargs):
        self.pos_score = kwargs["pos_score"]
        self.neg_score = kwargs["neg_score"]
        self.neu_score = kwargs["neu_score"]

    def __call__(self, score_dict):
        return self.pos_score*score_dict["pos"] + self.neg_score*score_dict["neg"] + self.neu_score*score_dict["neu"]


class SentimentAnalyser(ABC):

    @abstractmethod
    def analyse(self, clean_text):
        pass


class DefaultVaderAnalyser(SentimentAnalyser):
    def __init__(self):
        self.analyser = SentimentIntensityAnalyzer()

    def analyse(self, clean_text):
        return self.analyser.polarity_scores(clean_text)


class TextProcessor:
    def configure(self, ticker_searcher: TickerSearch, cleaner: TextCleaner, analyser: SentimentAnalyser, score_extractor: ScoreExtractor):
        self.ticker_searcher = ticker_searcher
        self.cleaner = cleaner
        self.analyser = analyser
        self.score_extractor = score_extractor

    def process(self, messy_text_body, id):
        tickers_in_text = self.ticker_searcher.search(messy_text_body)
        if tickers_in_text is NO_TICKER_ID:
            return {"id": id, "sentiment_score": nan, "tickers": NO_TICKER_ID}
        sentiment_score = self.score_extractor(self.analyser.analyse(self.cleaner.clean(messy_text_body)))
        return {"id": id, "sentiment_score": sentiment_score, "tickers": "_".join(tickers_in_text)}


if __name__ == "__main__":
    no_ticker_text = "Well I actually bought 100 shares on Friday. Sold a covered call 0dte for $5 and also sold 2 cash covered  0dte puts for about $45. \n\nThe puts expired about .15 away from the money and werenโ€t exercised so made more money just selling puts and will continue doing that."
    no_ticker_id = "no_ticker_id"

    ticker_text = "Well I actually bought 100 shares of TSLA on Friday. Sold a covered call 0dte for $5 and also sold 2 cash covered  0dte puts for about $45. \n\nThe puts expired about .15 away from the money and werenโ€t exercised so made more money just selling puts and will continue doing that."
    ticker_id = "ticker_id"

    text_and_ids = [(no_ticker_text, no_ticker_id), (ticker_text, ticker_id)]

    cleaner = TextCleaner()
    cleaner.configure()
    score_extractor = CompoundScore()
    sentiment_analyser = DefaultVaderAnalyser()
    ticker_search = TickerSearch()
    ticker_search.configure(tickers)

    processor = TextProcessor()
    processor.configure(ticker_search, cleaner, sentiment_analyser, score_extractor)
    for text, id in text_and_ids:
        print(processor.process(text, id))