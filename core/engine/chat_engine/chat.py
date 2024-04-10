import logging
import sys
import os

import openai
from dotenv import load_dotenv
load_dotenv()

from llama_index import (
   VectorStoreIndex,
   SimpleDirectoryReader,
   OpenAIEmbedding,
   PromptHelper,
   ServiceContext
)
from llama_index.indices.postprocessor import MetadataReplacementPostProcessor
from llama_index.storage.storage_context import StorageContext
from llama_index.node_parser import SentenceWindowNodeParser
from llama_index.vector_stores import ElasticsearchStore
from llama_index.postprocessor import SentenceTransformerRerank
from llama_index.schema import QueryBundle
from llama_index.llms import OpenAI
from llama_index.postprocessor import LLMRerank

from .prompts import REWRITE_QUERIES_TEMPLATE, text_qa_template

import time


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


os.environ['OPENAI_API_KEY'] = os.environ['OPENAI_API_KEY']

ES_CLOUD_ID = os.environ['ES_CLOUD']
ES_API_KEY = os.environ['ES_API']

openai.api_key = os.getenv('OPENAI_API_KEY')
llm = OpenAI(model="gpt-3.5-turbo")


class ChatEngine:

    def __init__(self, documents_path="./data/", new_indexing=False):
        self.vector_store = ElasticsearchStore(
                                index_name="law_bot",
                                es_cloud_id=ES_CLOUD_ID,
                                es_api_key=ES_API_KEY
        )
        self.node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )
        self.llm = OpenAI(model='gpt-3.5-turbo', temperature=0.7, max_tokens=256)
        self.embed_model = OpenAIEmbedding()
        self.prompt_helper = PromptHelper(
                                context_window=4096,
                                num_output=256,
                                chunk_overlap_ratio=0.1,
                                chunk_size_limit=None
                            )
        self.service_context = ServiceContext.from_defaults(
                                llm=llm,
                                embed_model=self.embed_model,
                                node_parser=self.node_parser,
                                prompt_helper=self.prompt_helper
                            )

        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            storage_context=self.storage_context,
            service_context=self.service_context
        )
        self.rerank = SentenceTransformerRerank(
            top_n = 3,
            model = "BAAI/bge-reranker-base"
        )
        if new_indexing:
            self.documents = SimpleDirectoryReader(documents_path).load_data()
            self.sentence_nodes = self.node_parser.get_nodes_from_documents(self.documents)
            self.index = VectorStoreIndex(
                self.sentence_nodes,
                storage_context=self.storage_context,
                service_context=self.service_context,
            )


    def chat_en(self, queries: list[str], query_origin):

        start_time = time.time()

        retriever = self.index.as_retriever(
            similarity_top_k=3,
            vector_store_query_mode="hybrid",
            alpha=0.5,
            text_qa_template = text_qa_template
        )

        # Get all node after retrieval step
        retrieved_nodes = []
        for query in queries:
            retrieved_nodes += retriever.retrieve(query)
        retrieved_nodes += retriever.retrieve(query_origin)

        # Remove objects with the same content
        seen_ids = set()
        retrieved_nodes = [obj for obj in retrieved_nodes if obj.get_score() > 0.5 and obj.get_content() not in seen_ids and not seen_ids.add(obj.get_content())]
        print(len(retrieved_nodes))

        end_time = time.time()
        elapsed_retrieval_time = end_time - start_time

        # Rerank
        start_time = time.time()
        query_bundle = QueryBundle(query_origin)

        # # configure reranker
        # rerank = LLMRerank(
        #     choice_batch_size=5,
        #     top_n=3,
        # )

        # retrieved_nodes = rerank.postprocess_nodes(
        #     retrieved_nodes, query_bundle
        # )
        # retrieved_nodes = [node for node in retrieved_nodes if node.get_score() > 5]

        retrieved_nodes = self.rerank.postprocess_nodes(
            retrieved_nodes, query_bundle
        )
        retrieved_nodes = [node for node in retrieved_nodes if node.get_score() > 0.3]

        end_time = time.time()
        elapsed_rerank_time = end_time - start_time

        # Replace with sentence window node
        postprocessor = MetadataReplacementPostProcessor(
            target_metadata_key="window",
        )

        window_nodes = postprocessor.postprocess_nodes(retrieved_nodes)

        # Get references
        references = []
        for i in window_nodes:
            print('REFRENCES: \n')
            print(i.get_score())
            print(i.get_content())
            print('='*100)
            refer = {
                "score": i.get_score(),
                "content": i.get_content(),
                "fileName": i.metadata['file_name']
            }
            references.append(refer)


        # Generate response with top_k result
        start_time = time.time()
        context_str = "\n\n".join([r.get_content() for r in window_nodes])

        llm = OpenAI(model="gpt-3.5-turbo")
        response = llm.predict(
            text_qa_template, context_str=context_str, query_str=query_origin
        )

        print(response)
        end_time = time.time()
        elapsed_generate_time = end_time - start_time

        print(f"Retrieval time: {elapsed_retrieval_time}")
        print(f"Rerank time: {elapsed_rerank_time}")
        print(f"Generate response time: {elapsed_generate_time}")
        return response, references


def generate_queries(query: str, num_queries: int = 2):

   response = llm.predict(
      REWRITE_QUERIES_TEMPLATE, num_queries=num_queries, query=query
   )

   queries = response.split("\n")
   queries_str = "\n".join(queries)
   print(f"Generated queries:\n{queries_str}")
   print("="*100)

   return queries



# if __name__ == "__main__":
#     query = "Các cơ sở của trường đại học Tôn Đức Thắng?"
#     queries = generate_queries(query)
#     chat = ChatEngine().chat(queries, query)

#     print(chat)