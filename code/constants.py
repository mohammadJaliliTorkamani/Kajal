PIPELINE_OUTPUT_PATH = './output.json'
INPUT_DATA_PATH = "EVALUATION SET JSON FILE PATH GOES HERE"
FSL_DATA_PATH = "FSL SET JSON FILE PATH GOES HERE"
OPENAI_API_KEY = "GPT API KEY GOES HERE"
OPENAI_LLM_MAX_TRIAL = 3
LLM_MODEL = 'gpt-3.5-turbo'
LLM_PRESENCE_PENALTY = 0
LLM_FREQUENCY_PENALTY = 0
LLM_TRIAL_GAP_SECONDS = 3
MAX_TOKEN_NUMBER = 16385
LLM_TEMPERATURE = 1
LLM_TOP_P = 1
LLM_RESPONSE_ERROR_SIGNS = ["Traceback (most recent call last)", "Bad gateway"]
MAX_FEEDBACK_TRIAL_NUMBER = 10
SYSTEM_FIELD = """
You are an expert in generating Lark grammars for code snippets. You are provided with a code snippet (enclosed within <CODE> and </CODE> tags). Optionally, you may also receive the last error message from parsing the code (enclosed within <MSG> and </MSG> tags) and a buggy grammar (enclosed within <BUGGY_GRAMMAR> and </BUGGY_GRAMMAR> tags). Your task is to generate a complete, error-free Lark grammar that can parse the given code code. Ensure that:

All non-terminals, tokens, and rules required to parse the snippet are fully defined.
The grammar is free from ambiguity or undefined symbols.
The grammar is minimal but sufficient to parse the provided code without errors.
Output only the corrected grammar, enclosed within <GRAMMAR> and </GRAMMAR> tags. Do not include any additional explanations or content.
"""
LARK_PARSER = 'lalr'
ENCLOSING_GRAMMAR_TAG = ["<GRAMMAR>", "</GRAMMAR>"]
CODE_ENCLOSING_TAGS = ["<CODE>", "</CODE>"]
FEEDBACK_ENCLOSING_TAGS = ["<MSG>", "</MSG>"]
BUGGY_GRAMMAR_ENCLOSING_TAGS = ["<BUGGY_GRAMMAR>", "</BUGGY_GRAMMAR>"]
MAX_NUMBER_OF_SIMILAR_RECORDS = 0
SIMILAR_RECORDS_THRESHOLD = 0.5
JSON_SOURCE_KEY = 'SOURCE'
JSON_GRAMMAR_KEY = 'GRAMMAR'
BERT_MODEL = 'bert-base-nli-mean-tokens'
