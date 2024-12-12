import datetime
import re

import constants
import utils
from grammar_tester import GrammarHandler
from llm import LLM
from similar_method_extractor import SimilarCodeExtractor


class Pipeline:
    def __init__(self, input_dataset: list, fsl_dataset: list):
        self.input_dataset = input_dataset
        self.fsl_dataset = fsl_dataset
        self.llm = LLM(constants.LLM_MODEL)
        self.similar_code_extractor = SimilarCodeExtractor(self.fsl_dataset)
        self.grammar_handle = GrammarHandler(constants.LARK_PARSER)

    def run(self):
        results = []
        for idx, record in enumerate(self.input_dataset):
            print(f"record {idx + 1} of {len(self.input_dataset)}")
            record_source = record[constants.JSON_SOURCE_KEY]
            utils.print_nested("extracting similar grammars...", 1)
            similar_records = self.similar_code_extractor.extract(record_source,
                                                                  constants.MAX_NUMBER_OF_SIMILAR_RECORDS,
                                                                  constants.SIMILAR_RECORDS_THRESHOLD)
            utils.print_nested("making inference...", 1)
            inferred_grammar, is_valid, is_correct, parse_tree, llm_input, llm_outputs, feedbacks = self.inference_record(
                record_source, similar_records)
            utils.print_nested(
                f"grammar {'extracted' if is_valid else 'could not be extracted.'} (Feedback size: {len(feedbacks)})",
                1)
            if is_valid:
                utils.print_nested(f"Grammar Correctness: {is_correct}", 2)

            results.append(
                (record, inferred_grammar, is_valid, is_correct, parse_tree, llm_input, llm_outputs, feedbacks))

        return results

    def analyze(self, raw_outputs):
        to_return = dict()
        dictionaries = list()
        to_return['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        to_return['total_number_of_items'] = len(self.input_dataset)

        isr_matrix = dict()
        for i in range(constants.MAX_FEEDBACK_TRIAL_NUMBER):
            isr_matrix[i + 1] = 0

        correct_inferences = 0
        valid_inferences = 0
        for raw_output in raw_outputs:
            record, inferred_grammar, is_valid, is_correct, parse_tree, llm_input, llm_outputs, feedbacks = raw_output

            dictionary = dict()
            dictionary['record'] = record
            dictionary['inferred_grammar'] = inferred_grammar
            dictionary['llm_input'] = llm_input
            dictionary['llm_raw_outputs'] = llm_outputs
            dictionary['feedbacks'] = feedbacks
            dictionary['is_valid_grammar'] = is_valid
            dictionary['is_correct_grammar'] = is_correct
            dictionary['parse_tree'] = str(parse_tree) if parse_tree else None
            valid_inferences += (1 if is_valid else 0)
            correct_inferences += (1 if is_correct else 0)

            if dictionary['is_valid_grammar']:
                isr_matrix[len(feedbacks) + 1] += 1

            dictionaries.append(dictionary)

        to_return['valid_inferences'] = valid_inferences
        to_return['correct_inferences'] = correct_inferences
        to_return['invalid_inferences'] = len(raw_outputs) - valid_inferences
        to_return['incorrect_inferences'] = len(raw_outputs) - correct_inferences
        to_return['validity_accuracy'] = 100.0 * valid_inferences / len(self.input_dataset)
        to_return['correctness_accuracy'] = 100.0 * correct_inferences / len(self.input_dataset)
        to_return['correctness_isr_matrix'] = isr_matrix
        to_return['items'] = dictionaries
        return to_return

    def inference_record(self, record_source, similar_records: list[dict]):
        counter = constants.MAX_FEEDBACK_TRIAL_NUMBER
        user_prompts = []
        assistant_prompts = []

        llm_feedback = None
        llm_feedbacks = []
        inferred_grammar = None
        llm_input = None
        llm_outputs = list()

        system_field = constants.SYSTEM_FIELD
        for record in similar_records:
            user_prompts.append(constants.CODE_ENCLOSING_TAGS[0] + "\n" + record[constants.JSON_SOURCE_KEY] + "\n" +
                                constants.CODE_ENCLOSING_TAGS[1])
            assistant_prompts.append(
                constants.ENCLOSING_GRAMMAR_TAG[0] + "\n" + record[constants.JSON_GRAMMAR_KEY] + "\n" +
                constants.ENCLOSING_GRAMMAR_TAG[1])

        while counter > 0:
            counter -= 1
            user_field = self.create_user_prompt(record_source, llm_feedback, inferred_grammar)

            user_prompts.append(user_field)

            llm_input, llm_output = self.llm.inference(user_prompts, assistant_prompts, system_field)
            assistant_prompts.append(llm_output)
            llm_outputs.append(llm_output)

            inferred_grammar = self.extract_grammar(llm_output)
            if inferred_grammar:
                if self.grammar_handle.is_parsable(inferred_grammar, record_source):
                    return (inferred_grammar,
                            self.grammar_handle.is_valid_grammar(inferred_grammar),
                            self.grammar_handle.is_parsable(inferred_grammar, record_source),
                            self.grammar_handle.get_parse_tree(inferred_grammar, record_source),
                            llm_input,
                            llm_outputs,
                            llm_feedbacks)
                else:
                    llm_feedback = self.grammar_handle.extract_parsing_error(inferred_grammar, record_source)
                    llm_feedbacks.append(llm_feedback)

            if counter > 0:
                print(
                    f"Error during grammar inference... Trying again ({constants.MAX_FEEDBACK_TRIAL_NUMBER - counter} of {constants.MAX_FEEDBACK_TRIAL_NUMBER})")

        print(
            f"Error during grammar inference... ({constants.MAX_FEEDBACK_TRIAL_NUMBER - counter} of {constants.MAX_FEEDBACK_TRIAL_NUMBER})")
        return inferred_grammar, False, False, None, llm_input, llm_outputs, llm_feedbacks

    def create_user_prompt(self, record_source, feedback, last_inferred_grammar):
        output = (f"{constants.CODE_ENCLOSING_TAGS[0]}\n"
                  f"{record_source}"
                  f"{constants.CODE_ENCLOSING_TAGS[1]}\n")
        if feedback:
            output += (constants.FEEDBACK_ENCLOSING_TAGS[0] + "\n" + feedback +
                       constants.FEEDBACK_ENCLOSING_TAGS[1] + "\n")

        if last_inferred_grammar:
            output += (constants.BUGGY_GRAMMAR_ENCLOSING_TAGS[0] + "\n" + last_inferred_grammar +
                       constants.BUGGY_GRAMMAR_ENCLOSING_TAGS[1] + "\n")

        return output

    def extract_grammar(self, llm_output):
        match = re.search(constants.ENCLOSING_GRAMMAR_TAG[0] + '(.*?)' + constants.ENCLOSING_GRAMMAR_TAG[1], llm_output,
                          re.DOTALL)
        if match:
            return match.group(1)
        return None
