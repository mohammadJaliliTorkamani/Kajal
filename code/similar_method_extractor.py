import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import warnings

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import constants


#
class SimilarCodeExtractor:

    def __init__(self, corpus):
        warnings.filterwarnings("ignore", category=FutureWarning)
        self.model = SentenceTransformer(constants.BERT_MODEL)
        self.dataset = corpus

    def extract(self, input_str: str, quantity, cosine_threshold) -> list[dict]:
        input_vector = self.model.encode(input_str)

        similar_records = []

        for record in self.dataset:
            if constants.JSON_SOURCE_KEY in record and constants.JSON_GRAMMAR_KEY in record:
                record_source_value = record[constants.JSON_SOURCE_KEY]
                record_grammar_value = record[constants.JSON_GRAMMAR_KEY]

                record_nl_vector = self.model.encode(record_source_value)
                similarity = cosine_similarity([input_vector], [record_nl_vector])

                if similarity >= cosine_threshold:
                    if len(similar_records) < quantity:
                        similar_records.append(
                            {constants.JSON_SOURCE_KEY: record_source_value,
                             constants.JSON_GRAMMAR_KEY: record_grammar_value})

                    else:
                        break

        return similar_records
