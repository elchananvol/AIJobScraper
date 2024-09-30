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
        self.thread = self.client.beta.threads.create()

    def __submit_message_to_thread(self, user_message):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id, role="user", content=user_message
        )
        return self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id,
        )

    def __get_thread_messages(self):
        return self.client.beta.threads.messages.list(thread_id=self.thread.id, order="desc")

    def __create_thread(self):
        thread = self.client.beta.threads.create()
        return thread

    @staticmethod
    def pretty_print(messages):
        print("# Messages")
        for m in messages:
            print(f"{m.role}: {m.content[0].text.value}")
        print()

    @staticmethod
    def get_user_messages(messages):
        return [m.content[0].text.value for m in messages if m.role == "assistant"]

    def wait_on_run(self, run):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id,
            )
            time.sleep(1)
        return run

    def submit_message(self, msg):
        run = self.__submit_message_to_thread(msg)
        self.wait_on_run(run)
        return OpenAIAssistant.get_user_messages(self.__get_thread_messages())[0]

# if __name__ == "__main__":
#     api_key = "sk"
#     assistant_name = "Math Tutor"
#     instructions = ""
#     # instructions = """You are coordinating professional resumes.
#     #  Answer with 'yes' or 'no' or 'maybe' and provide an explanation.
#     #  If there is any doubt, the answer should be 'maybe'."""
#     model = "gpt-4o-mini"
#
#     assistant = OpenAIAssistant(api_key, assistant_name, instructions, model)
#     print(assistant.assistant.id)
#     print(assistant.submit_message("how are you"))
#     print(assistant.submit_message("bla bla"))
#     print(assistant.submit_message("what is the average weather in new york in August"))
