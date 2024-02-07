# encoding=utf-8
import argparse
import os
import pickle

from openai import AzureOpenAI, OpenAI
from tqdm import tqdm


# this python script is used to generate the embedding of the input file or folder

class Embedding():
    def __init__(self, model="text-embedding-ada-002", api_type="open_ai", api_base=None, api_key=None,
                 api_version=None):
        if (api_type != "open_ai") and (api_type != "azure"):
            raise Exception("api_type should be open_ai or azure")

        self.model = model
        if api_type == "open_ai":
            self.client = OpenAI(api_key=api_key)
        elif api_type == "azure":
            self.client = AzureOpenAI(azure_endpoint=api_base, api_key=api_key, api_version=api_version)

    # return embedding of the input text
    def __call__(self, text):
        return self.get_embedding([text])

    # return embedding of the input text list
    def get_embedding(self, input_text_list):
        # if input_text_list is not a list throw an exception
        if not isinstance(input_text_list, list):
            raise TypeError("input_text_list should be a list")

        embedding = self.client.embeddings.create(
            model=self.model,
            input=input_text_list,
        )
        return [(text, data.embedding) for text, data in
                zip(input_text_list, embedding.data)], embedding.usage.total_tokens

    def get_raw_embedding(self, raw_text: str):
        embedding = self.client.embeddings.create(
            model=self.model,
            input=raw_text,
        )

        return list(embedding.data[0].embedding)

    def create_embeddings(self, input_text_list):
        # if input_text_list is not a list throw an exception
        if not isinstance(input_text_list, list):
            raise TypeError("input_text_list should be a list")

        result = []
        lens = [len(text) for text in input_text_list]
        query_len = 0
        start_index = 0
        tokens = 0

        for index, l in tqdm(enumerate(lens)):
            query_len += l
            if query_len > 4096:
                ebd, tk = self.get_embedding(input_text_list[start_index:index + 1])
                query_len = 0
                start_index = index + 1
                tokens += tk
                result.extend(ebd)

        if query_len > 0:
            ebd, tk = self.get_embedding(input_text_list[start_index:])
            tokens += tk
            result.extend(ebd)
        return result, tokens

    def create_embeddings_from_text(self, text: str):
        # if text is not a string throw an exception
        if not isinstance(text, str):
            raise TypeError("text should be a string")

        return self.create_embeddings([text.strip() for text in text.splitlines() if text.strip()])

    def create_embedding_from_file(self, input_file, output_file=None):
        # if input_file is not a file throw an exception
        if not os.path.isfile(input_file):
            raise TypeError("input_file should be a file")

        with open(input_file, "r", encoding='utf-8') as f:
            texts = f.readlines()
            texts = [text.strip() for text in texts if text.strip()]
            embeddings, tokens = self.create_embeddings(texts)

        if output_file == None:
            return embeddings
        else:
            # pickle the embeddings
            with open(output_file, "wb") as f:
                pickle.dump(embeddings, f)

    def create_embedding_from_file_save_to_file(self, input_file, output_file):
        # if input_file is not a file throw an exception
        if not os.path.isfile(input_file):
            raise TypeError("input_file should be a file")

        with open(input_file, "r") as f:
            with open(output_file, "w") as of:
                of.write(self.create_embeddings(f.readlines()))


# unit tests
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="input file")
    parser.add_argument("--output", type=str, required=False, help="output file")
    parser.add_argument("--model", type=str, default="text-embedding-ada-002", help="model name")
    args = parser.parse_args()

    # embedding = Embedding(model=args.model)
    # print(embedding.create_embeddings(args.input))
    # print(embedding("hello world"))
    # print(embedding.create_embedding_from_file(args.input, args.output))
    # print(embedding.create_embedding_from_file_save_to_file(args.input, args.output))

    use_openai = False
    if use_openai:
        # test for openai
        embedding = Embedding()
    else:
        # test for azure
        embedding = Embedding(
            model=os.getenv("AZURE_OPENAI_MODEL"),
            api_type="azure",
            api_base=os.getenv("AZURE_OPENAI_API_BASE"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )

    print(embedding.create_embeddings_from_text(args.input))
    print(embedding.get_raw_embedding(args.input))
