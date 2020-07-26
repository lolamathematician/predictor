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
import configparser

tickers = {0: "TSLA",
           1: "MSFT"}

NO_TICKER_ID = "NO_TICKER"


class TickerSearch:
    def __init__(self, ticker_list):
        self.ticker_list = ticker_list
        self.automaton = ahocorasick.Automaton()
        for ticker_index, ticker in enumerate(ticker_list):
            self.automaton.add_word(ticker, ticker_index)
        self.automaton.make_automaton()

    def search(self, messy_text_body):
        tickers_in_text = [self.ticker_list[ticker_index] for (_, ticker_index) in self.automaton.iter(messy_text_body)]
        if not tickers_in_text:
            return NO_TICKER_ID
        return tickers_in_text


class TextCleaner:
    def __init__(self, tokeniser, lemmatiser):
        self.stopwords = stopwords.words('english')
        self.tokeniser = tokeniser
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
    def __init__(self, ticker_searcher: TickerSearch, cleaner: TextCleaner,
                 analyser: SentimentAnalyser, score_extractor: ScoreExtractor):
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


def ticker_search_constructor(key):
    available_tickers = ["TSLA", "MSFT", "APPL"]  # ETC
    if key == "ALL":
        return TickerSearch(available_tickers)
    tickers_from_key = key.split(",")
    for ticker in tickers_from_key:
        if ticker not in available_tickers:
            raise KeyError("{} is not a valid ticker!".format(ticker))
    return TickerSearch(tickers_from_key)


def tokeniser_constructor(key):
    tokeniser_dict = {"REGEXP_WORDS": RegexpTokenizer(r'\w+')}
    try:
        return tokeniser_dict[key]
    except KeyError as error:
        raise


def lemmatiser_constructor(key):
    lemmatiser_dict = {"WORDNET": WordNetLemmatizer()}
    try:
        return lemmatiser_dict[key]
    except KeyError as error:
        raise


def scorer_constructor(key):
    # TODO INCORPORATE WEIGHTS
    scorer_dict = {"DIRAC": DiracScore(),
                   "COMPOUND": CompoundScore(),
                   "POSITIVE": PositiveScore(),
                   "NEGATIVE": NegativeScore(),
                   "NEUTRAL": NeutralScore()}
    try:
        return scorer_dict[key]
    except KeyError as error:
        raise


def analyser_constructor(key):
    anaylser_dict = {"DEFAULT_VADER": DefaultVaderAnalyser()}
    try:
        return anaylser_dict[key]
    except KeyError as error:
        raise


def construct_text_processing_pipeline(mode):
    config = configparser.ConfigParser()
    config.read('./resources/text_processing.ini')
    process_cfg = config[mode]
    ticker_searcher = ticker_search_constructor(process_cfg["TICKERS"])
    tokeniser = tokeniser_constructor(process_cfg["TOKENISER"])
    lemmatiser = lemmatiser_constructor(process_cfg["LEMMATISER"])
    scorer = scorer_constructor(process_cfg["SCORER"])
    analyser = analyser_constructor(process_cfg["ANALYSER"])
    cleaner = TextCleaner(tokeniser=tokeniser, lemmatiser = lemmatiser)
    return TextProcessor(ticker_searcher=ticker_searcher, cleaner=cleaner, analyser=analyser, score_extractor=scorer)


def test(mode):
    no_ticker_text = "Well I actually bought 100 shares on Friday. Sold a covered call 0dte for $5 and also sold 2 cash covered  0dte puts for about $45. \n\nThe puts expired about .15 away from the money and werenโ€t exercised so made more money just selling puts and will continue doing that."
    no_ticker_id = "no_ticker_id"

    ticker_text = "Well I actually bought 100 shares of TSLA on Friday. Sold a covered call 0dte for $5 and also sold 2 cash covered  0dte puts for about $45. \n\nThe puts expired about .15 away from the money and werenโ€t exercised so made more money just selling puts and will continue doing that."
    ticker_id = "ticker_id"

    text_and_ids = [(no_ticker_text, no_ticker_id), (ticker_text, ticker_id)]

    test_processor = construct_text_processing_pipeline(mode)
    for text, id in text_and_ids:
        print(test_processor.process(text, id))


if __name__ == "__main__":
    test("STANDARD")

