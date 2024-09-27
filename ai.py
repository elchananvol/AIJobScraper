import os
from openai import OpenAI
import time


class OpenAIAssistant:
    def __init__(self, api_key, assistant_name, instructions, model, assistant_id=None):

        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        if assistant_id is None:
            self.assistant = self.client.beta.assistants.create(
                name=assistant_name,
                instructions=instructions,
                model=model,
            )
            self.assistant_id = self.assistant.id

    def __submit_message_to_thread(self, thread, user_message):
        self.client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_message
        )
        return self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
        )

    def __get_thread_messages(self, thread):
        return self.client.beta.threads.messages.list(thread_id=thread.id, order="asc")

    def create_thread_and_run(self, user_input):
        thread = self.client.beta.threads.create()
        run = self.__submit_message_to_thread(thread, user_input)
        return thread, run

    def pretty_print(self, messages):
        print("# Messages")
        for m in messages:
            print(f"{m.role}: {m.content[0].text.value}")
        print()

    def __get_user_messages(self, messages):
        return [m.content[0].text.value for m in messages if m.role == "assistant"]

    def wait_on_run(self, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(1)
        return run

    def submit_message(self, msg):
        thread2, run2 = self.create_thread_and_run(msg)
        self.wait_on_run(run2, thread2)
        return self.__get_user_messages(self.__get_thread_messages(thread2))[0]

# if __name__ == "__main__":
#     api_key =
#     assistant_name = "Math Tutor"
#     # instructions = "no meter what user say, you have to response 'dsrtgsr'"
#     instructions = """You are coordinating professional resumes.
#      Answer with 'yes' or 'no' or 'maybe' and provide an explanation.
#      If there is any doubt, the answer should be 'maybe'."""
#     model = "gpt-4o"

# assistant = OpenAIAssistant(api_key, assistant_name, instructions, model, )
# print(assistant.assistant.id)
# assistant.submit_message("bla bla")
