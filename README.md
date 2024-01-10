# Poem Api for the ML6 Software Engineer challenge

The api can generate poems via a large language model and return them either as plain text or as synthesized audio.

## Google cloud services used

* [Vertex AI API](https://cloud.google.com/vertex-ai/?hl=en) for generating the poems via the Gemini model
* [Text-to-Speech API](https://cloud.google.com/text-to-speech/?hl=en) for synthesizing the poems to speech
* [Secret Manager API](https://cloud.google.com/security/products/secret-manager) for securely storing the API key

## Run locally

Install dev requirements via 

    python -m pip install -r requirements-dev.txt

Run via 
    
    python main.py

Run the tests via 

    python -m pytest

## Deploy to Google Cloud

    gcloud run deploy --source .

## Usage

The Api serves get requests for generating poems as plain text and as synthesized audio. 

Assuming that the API is running locally (for the cloud, the URL has to be adapted accordingly), the base uris for this are:

* Generating poems as plain text: http://localhost:8000/print_poem
* Generating poems as audio: http://localhost:8000/read_poem

Both variants share the following parameters:

* `api_key` (required): The api key for accessing the api 
* `language` (required): The language in which the poem should be generated as IETF language tag
* `max_length` (optional, defaults to 12): The maximum length of the poem (in lines)
* `topic` (optional, if not given, the topic will be choosen by the LLM): The topic the poem should be about

For `read_poem`, there's the following additional parameter:

* `gender` (optional, "unspecified" is used as default): The gender of the text to speech voice to use ("female", "male" or "unspecified")

For example for generating a poem about Gent in Flemish, with a maximum length of 10 lines and read by a female voice, the request would look as follows:

    http://localhost:8000/read_poem?language=nl-BE&topic=Gent&gender=female&max_length=10&api_key=<insert api key>

