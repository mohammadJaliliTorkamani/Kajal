import time

from openai import OpenAI
from openai.types.chat import ChatCompletion

import constants
import utils


class LLM:
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI(api_key=constants.OPENAI_API_KEY)
        assert constants.OPENAI_LLM_MAX_TRIAL >= 1

    def extract_message(self, response: ChatCompletion) -> str | None:
        try:
            return response.choices[0].message.content
        except Exception:
            return None

    def inference(self, users: list, assistants: list, system: str) -> (str, str | None):
        input_message = [{'role': 'system', 'content': system}]

        for (u, a) in zip(users, assistants):
            input_message.append(
                {'role': 'user',
                 'content': u})
            input_message.append(
                {'role': 'assistant',
                 'content': a})
        input_message.append(
            {'role': 'user',
             'content': users[-1]})

        trial_number = constants.OPENAI_LLM_MAX_TRIAL
        while trial_number > 0:
            try:
                response = self.client.chat.completions.create(model=self.model, temperature=constants.LLM_TEMPERATURE,
                                                               top_p=constants.LLM_TOP_P, stream=False,
                                                               presence_penalty=constants.LLM_PRESENCE_PENALTY,
                                                               frequency_penalty=constants.LLM_FREQUENCY_PENALTY,
                                                               messages=input_message
                                                               )
                output_message = self.extract_message(response)
                if output_message is not None and utils.is_not_in_list(constants.LLM_RESPONSE_ERROR_SIGNS,
                                                                       output_message):
                    return input_message, output_message
                else:
                    trial_number -= 1
            except Exception as e:
                utils.print_nested(str(e))
                trial_number -= 1

            utils.print_nested(f"invalid LLM response. Trying again after {constants.LLM_TRIAL_GAP_SECONDS} "
                               f"seconds...", 1)
            time.sleep(constants.LLM_TRIAL_GAP_SECONDS)

        raise Exception("Error while doing inference")
