from dotenv import load_dotenv
import os
import openai
from pydub import AudioSegment
from pydub.playback import play
import logging
import tempfile
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

load_dotenv()
AudioSegment.converter = "/usr/local/bin/ffmpeg"
logger = logging.getLogger(__name__)
client = openai.OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))


def index(request):
    template = loader.get_template("food_logs/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


@csrf_exempt
def transcribe_and_analyze(request):
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]

        try:
            # Log audio file info
            logger.info(f"Received audio file: {audio_file.name}, size: {audio_file.size} bytes")

            # Convert webm to mp3
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
                audio = AudioSegment.from_file(audio_file, format="webm")
                audio.export(temp_audio_file.name, format="mp3")
                logger.info(f"Converted audio saved to: {temp_audio_file.name}")

                with open(temp_audio_file.name, "rb") as openai_audio:
                    transcription = client.audio.transcriptions.create(model="whisper-1", file=openai_audio, response_format="text")
                    transcript = transcription
                    print(transcript)
        except Exception as e:
            logger.error(f"Error during audio processing: {str(e)}")
            return JsonResponse({"message": f"Error during audio processing: {str(e)}"}, status=500)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_file.name):
                os.remove(temp_audio_file.name)

        prompt = f"Estimate the total calories for the following food description: {transcript}"
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            gpt_response = completion.choices[0].message
            print(gpt_response)
            calories = gpt_response.content
        except Exception as e:
            logger.error(f"Error during ChatGPT analysis: {str(e)}")
            return JsonResponse({"message": f"Error during ChatGPT analysis: {str(e)}"}, status=500)

        return JsonResponse({"message": calories})

    return JsonResponse({"message": "Invalid request"}, status=400)