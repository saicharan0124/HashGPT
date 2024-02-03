from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Body, APIRouter, Depends, BackgroundTasks
import httpx
import requests
from httpx import HTTPError
from nltk.tokenize import sent_tokenize
import nltk
from urllib.parse import urlparse
from haystack.document_stores import WeaviateDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser, BM25Retriever
from haystack.pipelines import Pipeline
from app.database import db_config
from app.auth import auth_bearer
from typing import Union, List
from app.schema import model
import asyncio
from collections import defaultdict
from fastapi_utils.tasks import repeat_every
from decouple import config



router = APIRouter()
doc_collection, users_collection = db_config.init_db()


# Download NLTK punkt data if not already downloaded
nltk.download('punkt', quiet=True)
openai_api_key = config("openai_key")


async def run_query(host, slug):

    query = f"""
    {{
        publication(host: "{host}") {{
            isTeam
            title
            post(slug: "{slug}") {{
                title
                content {{
                    text
                }}
            }}
        }}
    }}
    """

    async with httpx.AsyncClient() as client:
        response = await client.post("https://gql.hashnode.com/", json={'query': query})

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail=f"Query failed to run by returning code of {response.status_code}.")


async def get_all_posts(host: str):

    query = f"""
    {{
        publication(host: "{host}") {{
            posts(first: 4) {{
                edges {{
                    node {{
                        id
                        title
                        subtitle
                        slug
                        content {{
                            text
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    async with httpx.AsyncClient() as client:
        response = await client.post("https://gql.hashnode.com/", json={'query': query})

        return response.json()


async def get_posts_comments(host: str, post_slug: str):

    query = f"""
    {{
        publication(host: "{host}") {{
            post(slug: "{post_slug}") {{
                comments(first: 20) {{
                    totalDocuments
                    edges {{
                        node {{
                            id
                            content {{
                                text
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    async with httpx.AsyncClient() as client:
        response = await client.post("https://gql.hashnode.com/", json={'query': query})

        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse response JSON: {e}")
        else:
            raise HTTPException(status_code=500, detail=f"Query failed to run by returning code of {response.status_code}")


async def add_comment(comment_id, content, api_key):
    url = "https://gql.hashnode.com/"  # Replace with your GraphQL endpoint

    mutation = f"""
    mutation AddComment {{
      addReply(input: {{
        commentId: "{comment_id}",
        contentMarkdown: "{content}"
      }}) {{
        reply {{
          id
        }}
      }}
    }}
    """

    headers = {
        'Content-Type': 'application/json',
        "Authorization": api_key
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={'query': mutation}, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500,
                                detail=f"Query failed to run by returning code of {response.status_code}")


def split_into_sentences(text):
    sentences = sent_tokenize(text)
    return sentences


@router.post("/add_document", tags=["core"])
async def add_document(url: str = Body(..., embed=True), user_data: Union[bool, str] = Depends(auth_bearer.JWTBearer())):
    # Extract host and slug from the URL
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    slug = parsed_url.path.lstrip('/')
    print(host)
    print(slug)
    # Run the query
    result = await run_query(host, slug)

    # Extract the text content from the result
    result_text = result["data"]["publication"]["post"]["content"]["text"]
    print(result_text)

    # Split the text into sentences
    sentences = split_into_sentences(result_text)
    print(sentences)

    # Create a list of dictionaries where each dictionary represents a document
    documents = [{"content": sentence, "meta": {"sentence_index": i}} for i, sentence in enumerate(sentences, 1)]
    username = user_data.split('@')[0]
    # Create a Weaviate Document Store
    ds = WeaviateDocumentStore(host="http://localhost", port=8080, embedding_dim=768, index=username)

    # Write documents to Weaviate Document Store
    ds.write_documents(documents)

    # Create an EmbeddingRetriever with Weaviate Document Store and Sentence Transformer Model
    retriever = EmbeddingRetriever(document_store=ds, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")

    # Update embeddings in Weaviate Document Store
    ds.update_embeddings(retriever)

    return {"documents_added": len(documents)}


@router.post("/answergen", tags=["core"])
async def generate_answer(query: str = Body(..., embed=True), user_data: Union[bool, str] = Depends(auth_bearer.JWTBearer())):
    print("Start of function")

    prompt_template = PromptTemplate(
        prompt="""
        Answer the question truthfully based solely on the given documents. If the documents do not contain the answer to the question, say that answering is not possible given the available information.
        Additionally, provide a clear explanation and also alway complete your answer meaningfully.
        Documents:{join(documents)}
        Question:{query}
        Answer:
        """,
        output_parser=AnswerParser(),
    )

    print("Prompt template created")

    prompt_node = PromptNode(
        model_name_or_path="gpt-3.5-turbo-instruct", api_key=openai_api_key, default_prompt_template=prompt_template
    )

    print("Prompt node created")
    username = user_data.split('@')[0]

    ds = WeaviateDocumentStore(host="http://localhost", port=8080, embedding_dim=768, index=username)
    try:
        retriever = EmbeddingRetriever(document_store=ds, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
        print("Retriever created successfully")
    except Exception as e:
        print(f"Error creating retriever: {e}")

    print("Document store and retriever created")

    generative_pipeline = Pipeline()
    generative_pipeline.add_node(component=retriever, name="retriever", inputs=["Query"])
    generative_pipeline.add_node(component=prompt_node, name="prompt_node", inputs=["retriever"])

    print("Pipeline created")

    response = generative_pipeline.run(query)

    print("End of function")

    return {"response": response}


@router.post("/replyrover", tags=["core"])
async def reply_rover(inputs:model.ReplyRoverInput, user_data: Union[bool, str] = Depends(auth_bearer.JWTBearer())):

    data = await get_all_posts(inputs.host)
    # print(data)
    slugs = []
    contents = []
    edges = data['data']['publication']['posts']['edges']
    for post in edges:
        node = post['node']

        # Accessing title and slug

        slug = node['slug']

        slugs.append(slug)

        # Accessing content
        content = node['content']['text']
        contents.append(content)
        sentences = []
        for i in contents:

            sentences.extend(split_into_sentences(i))

    # sentences = split_into_sentences(content)
    documents = [{"content": sentence, "meta": {"sentence_index": i}} for i, sentence in enumerate(sentences, 1)]
    # print(documents)
    username = user_data.split('@')[0]
    # Create a Weaviate Document Store
    ds = WeaviateDocumentStore(host="http://localhost", port=8080, embedding_dim=768, index=username)

    # Write documents to Weaviate Document Store
    ds.write_documents(documents)

    # Create an EmbeddingRetriever with Weaviate Document Store and Sentence Transformer Model
    retriever = EmbeddingRetriever(document_store=ds,
                                   embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")

    # Update embeddings in Weaviate Document Store
    ds.update_embeddings(retriever)

    doc_dict = {
        "owner": user_data,
        "host": inputs.host,
        "slug":  slugs,
        "api_key": inputs.api_key,
        "last_comment": []
    }
    doc_collection.insert_one(doc_dict)
    return {"Done!"}


async def worker():
    host_slugs_map = defaultdict(list)
    for doc in doc_collection.find():
        host = doc.get("host")
        slug = doc.get("slug")
        api_key = doc.get("api_key")
        owner = doc.get("owner")
        if host and slug:
            host_slugs_map[host].append(slug)

    for host, slugs in host_slugs_map.items():
        for slug in slugs:
            # Call the get_posts_comments function for each host and slug
            print(host, slug)

            if isinstance(slug, str):
                # If there's only one slug (string), call the function directly
                result = await get_posts_comments(host, slug)
                await process_comments(result, host, individual_slug, owner, api_key)
                print(result)
            elif isinstance(slug, list):
                # If there are multiple slugs (list), iterate over them and call the function
                for individual_slug in slug:
                    result = await get_posts_comments(host, individual_slug)
                    await process_comments(result, host, individual_slug, owner, api_key)
                    # Process the result as needed
                    print(result)


async def process_comments(result, host, slug, owner, api_key):
    # Extract comments from the result
    comments = result['data']['publication']['post']['comments']['edges']
    last_comment_doc = doc_collection.find_one({"owner": owner})
    last_comment = last_comment_doc.get("last_comment", [])

    # Iterate over each comment's id and content
    for index, comment in enumerate(comments, 1):
        comment_id = comment['node']['id']
        comment_text = comment['node']['content']['text']
        print(comment_id)
        print(comment_text)
        if not last_comment or comment_id not in last_comment:
            await answer_comment(comment_id, comment_text, owner, api_key)


async def answer_comment(comment_id, query, user_data, api_key ):
    # Create prompt template
    prompt_template = PromptTemplate(
        prompt="""
           Answer the question truthfully based solely on the given documents. If the documents do not contain the answer to the question, say that answering is not possible given the available information.
           Additionally, provide a clear explanation and also alway complete your answer meaningfully.
           Documents:{join(documents)}
           Question:{query}
           Answer:
           """,
        output_parser=AnswerParser(),
    )

    print("Prompt template created")

    # Create prompt node
    prompt_node = PromptNode(
        model_name_or_path="gpt-3.5-turbo-instruct", api_key=openai_api_key, default_prompt_template=prompt_template
    )

    print("Prompt node created")
    username = user_data.split('@')[0]

    # Create Weaviate Document Store
    ds = WeaviateDocumentStore(host="http://localhost", port=8080, embedding_dim=768, index=username)

    # Create EmbeddingRetriever
    retriever = EmbeddingRetriever(document_store=ds,
                                   embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")

    print("Document store and retriever created")

    # Create generative pipeline
    generative_pipeline = Pipeline()
    generative_pipeline.add_node(component=retriever, name="retriever", inputs=["Query"])
    generative_pipeline.add_node(component=prompt_node, name="prompt_node", inputs=["retriever"])

    response = generative_pipeline.run(query)
    first_answer = response['answers'][0].answer if response.get('answers') and response[
        'answers'] else 'No answer available'
    ai_response = f"Spit out by the AI word wizard!  '{first_answer}'"

    await add_comment(comment_id, ai_response, api_key )
    doc_collection.update_one(
        {"owner": user_data},
        {"$push": {"last_comment": comment_id}},
        upsert=True
    )


@repeat_every(seconds=60)
async def start_repeated_task():
    asyncio.create_task(worker())


async def startup():
    await start_repeated_task()

asyncio.create_task(startup())





