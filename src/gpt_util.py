from openai import OpenAI, AzureOpenAI


class OpenAIClient:
    def __init__(self, api_type="open_ai", api_base=None, api_key=None, api_version=None, chatModel=None):
        if (api_type != "open_ai") and (api_type != "azure"):
            raise Exception("api_type should be open_ai or azure")

        self.chatModel = chatModel
        if api_type == "open_ai":
            self.client = OpenAI(api_key=api_key)
        elif api_type == "azure":
            self.client = AzureOpenAI(azure_endpoint=api_base, api_key=api_key, api_version=api_version)

    def chatCompletionsCreate(self, temperature, messages):
        response = self.client.chat.completions.create(
            model=self.chatModel,
            temperature=temperature,
            messages=messages
        )

        return response.choices[0].message.content
