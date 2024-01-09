import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationResponse
from google.cloud.aiplatform_v1beta1.types.content import Candidate
from constants import PROJECT_ID, GENERATIVE_MODEL_LOCATION, GENERATIVE_MODEL_NAME 
from connexion.exceptions import InternalServerError

class PoemUtils:
    """
    Provides means to generate poems via the Google Cloud Vertex AI Gemini API.
    """
        
    _generative_model: GenerativeModel = None

    async def generate_poem(self, language: str, max_length: int, topic: str | None) -> str:
        """Generates a poem in the provided language with the provided maximum length, optionally about the provided topic.

        Args:
            language: The language as IETF language tag.
            max_length: The maximum length of the poem (in lines).
            topic: The topic the poem should be about. (optional)

        Returns:
            The generated poem.
        """
        prompt = self._build_prompt(language, max_length, topic)
        return await self._query_generative_model(prompt)


    def _build_prompt(self, language: str, max_length: int, topic: str | None) -> str:
        """Builds the prompt for querying the generative model.

        Args:
            language: The language as IETF language tag.
            max_length: The maximum length of the poem (in lines).
            topic: The topic the poem should be about. (optional)

        Returns:
            The prompt.
        """
        topic_part = "" if topic is None else f"about '{topic}' "
        return f"Generate a poem {topic_part}that rhymes in the language represented by the IETF language tag '{language}' with the maximum length of {max_length} lines."
        
    async def _query_generative_model(self, prompt: str) -> str:
        """Queries the generative model with the provided prompt and returns the resulting text.

        Args:
            prompt: The prompt for querying the model
        
        Returns:
            The resulting text.

        Raises:
            InternalServerError if the model fails to generate a text, e.g. because response doesn't contain any candidates or the FinishReason is not STOP.
        """
        print (f"querying generative model with prompt '{prompt}'")
        self._prepare_generative_model()    
        response: GenerationResponse = await self._generative_model.generate_content_async(prompt)
        print ("response: ", response)
        if not response.candidates:
            raise InternalServerError("generation failed, no candidates were returned")
        candidate: Candidate = response.candidates[0]
        if not candidate.finish_reason == Candidate.FinishReason.STOP:
            raise InternalServerError(f"generation failed, finish reason is not STOP but {candidate.finish_reason}")
        return candidate.text

    def _prepare_generative_model(self):
        """Intitializes the GenerativeModel if not yet done."""
        if self._generative_model is None:
            print("initializing generative model")
            vertexai.init(project=PROJECT_ID, location=GENERATIVE_MODEL_LOCATION)
            self._generative_model = GenerativeModel(GENERATIVE_MODEL_NAME)
            print("generative model initialized")
        else:
            print("generative model was already initialized")
