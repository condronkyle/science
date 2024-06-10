from openai import OpenAI

client = OpenAI()


class Assistant:
    def __init__(self, name, instructions):
        self.name = name
        self.instructions = instructions

    def create_assistant(self):
        assistant = client.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
        )
        return assistant.id


class PaperScorer(Assistant):
    def __init__(self, client):
        super().__init__(
            "PaperScorer",
            """
            You are an expect in understanding and disseminating information about scientific research.
            You have extensive knowledge on the latest trends, theories, and research areas of a variety of fields.
            Many different people trust your judgment.
            You are particularly appreciated for your ability to analyze new research and compare the results and methods.
            """,
        )
