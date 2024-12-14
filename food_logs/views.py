from dotenv import load_dotenv
import logging
import openai
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from pydub import AudioSegment
from django.shortcuts import render
from .models import FoodLog, Unit
from itertools import groupby

load_dotenv()
AudioSegment.converter = "/usr/local/bin/ffmpeg"
logger = logging.getLogger(__name__)
client = openai.OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))


@login_required
def index(request):
    return render(request, "food_logs/index.html")


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

        prompt = (
            f"Extract details for all foods mentioned in this text: {transcript}\n"
            f"Provide the details in JSON format with a 'foods' key, containing an array of objects with fields: "
            f"food_name, quantity, unit, calories, fat, carbs, sugar, fiber, protein, sodium."
            f"Try to ensure that the unit is in the following list: grams, kilograms, milliliters, liters, cups, tablespoons, teaspoons, ounces, pounds, pieces, slices, servings."
            f"If there is one apple, instead of responding with the unit as 'pieces' return 'pieces', do the same for similar units"
        )
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
            print(gpt_response.content)
            response_data = eval(gpt_response.content)
            foods = response_data.get("foods", [])
            if not foods:
                return JsonResponse({"message": "No foods found in the response."}, status=400)

            saved_food_logs = []
            for food_data in foods:
                unit_name = food_data.get("unit", "").lower()
                unit = Unit.objects.filter(name__iexact=unit_name).first()

                if not unit:
                    logger.warning(
                        f"Unit '{unit_name}' not found. Skipping food: {food_data.get('food_name', 'Unknown')}")
                    continue

                food_log = FoodLog.objects.create(
                    user=request.user,
                    food_name=food_data.get("food_name", "Unknown Food"),
                    quantity=food_data.get("quantity", 0),
                    unit=unit,
                    calories=food_data.get("calories", 0),
                    fat=food_data.get("fat", 0),
                    carbs=food_data.get("carbs", 0),
                    sugar=food_data.get("sugar", 0),
                    fiber=food_data.get("fiber", 0),
                    protein=food_data.get("protein", 0),
                    sodium=food_data.get("sodium", 0),
                )

                saved_food_logs.append({
                    "id": food_log.id,
                    "food_name": food_log.food_name,
                    "quantity": food_log.quantity,
                    "unit": food_log.unit.name,
                    "calories": food_log.calories,
                    "fat": food_log.fat,
                    "carbs": food_log.carbs,
                    "sugar": food_log.sugar,
                    "fiber": food_log.fiber,
                    "protein": food_log.protein,
                    "sodium": food_log.sodium,
                    "log_date": food_log.log_date,
                })

            if not saved_food_logs:
                return JsonResponse({"message": "No food logs could be saved."}, status=400)

            # Calculate totals
            total_calories = sum(item["calories"] for item in saved_food_logs)
            total_protein = sum(item["protein"] for item in saved_food_logs)
            total_carbs = sum(item["carbs"] for item in saved_food_logs)
            total_fat = sum(item["fat"] for item in saved_food_logs)

            message = f"Log created successfully for {transcript} " \
                      f"Total: {total_calories} calories, {total_protein}g protein, " \
                      f"{total_carbs}g carbs, {total_fat}g fat."

            # Respond with the saved food logs
            return JsonResponse({"message": message, "food_logs": saved_food_logs})
        except Exception as e:
            logger.error(f"Error during ChatGPT analysis: {str(e)}")
            return JsonResponse({"message": f"Error during ChatGPT analysis: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request"}, status=400)


@login_required
def view_logs(request):
    # Query all FoodLog entries for the logged-in user
    logs = FoodLog.objects.filter(user=request.user).order_by('-log_date')

    # Group logs by day
    grouped_logs = {}
    for key, group in groupby(logs, key=lambda log: log.log_date.date()):
        grouped_logs[key] = list(group)

    return render(request, 'food_logs/food_logs_list.html', {'grouped_logs': grouped_logs})
