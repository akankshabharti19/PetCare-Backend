from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, UserProfile, Pet
from .serializers import UserSerializer, PetSerializer, UserProfileSerializer
from mongoengine import DoesNotExist
from django.views.decorators.csrf import csrf_exempt

import requests
from pymongo import MongoClient
import os
from django.core.paginator import Paginator

client = MongoClient(os.environ.get("MONGODB_URI"))
db = client['pet_care']
breeds_collection = db['breeds']
images_collection = db['breed_images']


DOG_API_URL = "https://dog.ceo/api/breeds/list/all"
DOG_IMAGE_API_URL = "https://dog.ceo/api/breed/{breed}/images/random"
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
WEATHER_API_KEY = "88bb410e391a4615828130453242906"

# Predefined breed descriptions
BREED_DESCRIPTIONS = {
    "affenpinscher": "A small breed with a monkey-like expression, known for its playful and adventurous personality.",
    "african": "Typically refers to breeds native to Africa, such as the Africanis, known for their endurance and versatility.",
    "airedale": "The largest of the terrier breeds, known for their intelligence, loyalty, and protective nature.",
    "akita": "A large and powerful breed from Japan, known for their loyalty and courage.",
    "appenzeller": "A medium-sized herding dog from Switzerland, known for their agility and versatility.",
    "australian": "A versatile and intelligent herding dog, known for its loyalty and protective nature.",
    "bakharwal": "A livestock guardian dog from India, known for its strength and protective nature.",
    "basenji": "A small hunting dog from Africa, known for its independence and unique yodel-like bark.",
    "beagle": "A small scent hound, known for its friendly and curious nature.",
    "bluetick": "A breed of coonhound known for its hunting ability and distinctive blue mottled coat.",
    "borzoi": "A Russian sighthound known for its elegance, speed, and gentle temperament.",
    "bouvier": "A large herding dog known for its strength, versatility, and protective nature.",
    "boxer": "A medium to large breed known for its playful, energetic, and loyal nature.",
    "brabancon": "A small breed with a distinctive face, known for its affectionate and alert nature.",
    "briard": "A large herding dog known for its loyalty, intelligence, and protective instincts.",
    "buhund": "A versatile and energetic herding dog known for its agility and intelligence.",
    "bulldog": "A small breed known for its friendly and lively personality.",
    "bullterrier": "A medium-sized breed known for its strength, courage, and affectionate nature.",
    "cattledog": "An energetic and intelligent herding dog known for its stamina and work ethic.",
    "cavapoo": "A crossbreed between a Cavalier King Charles Spaniel and a Poodle, known for its friendly and affectionate nature.",
    "chihuahua": "The smallest dog breed, known for its bold and lively personality.",
    "chippiparai":  "A sighthound breed from India, known for its speed, endurance, and hunting skills.",
    "chow": "A medium to large breed known for its lion-like mane and independent nature.",
    "clumber": "A large and heavy-boned spaniel known for its gentle and affectionate nature.",
    "cockapoo": "A crossbreed between a Cocker Spaniel and a Poodle, known for its friendly and affectionate personality.",
    "collie":  "A highly intelligent and energetic herding dog known for its agility and work ethic.",
    "coonhound": "A group of scent hounds known for their hunting ability and distinctive baying voice.",
    "corgi":  "A small herding dog with a long body and fox-like appearance, known for its loyalty and intelligence.",
    "cotondetulear": "A small breed from Madagascar known for its cotton-like coat and cheerful personality.",
    "dachshund": "A small breed with a long body and short legs, known for its bold and curious nature.",
    "dalmatian": "A medium-sized breed known for its distinctive spotted coat and energetic personality.",
    "dane":  "One of the largest dog breeds, known for its gentle and friendly nature.",
    "danish": "Refers to the Danish-Swedish Farmdog, a small and versatile breed known for its working ability and friendly nature.",
    "deerhound":  "A large sighthound known for its gentle and dignified nature.",
    "dhole": "A wild canid from Asia, known for its social structure and hunting ability.",
    "dingo": "A wild dog from Australia, known for its independent and adaptable nature.",
    "doberman": "A large and powerful breed known for its loyalty, intelligence, and protective nature.",
    "elkhound": "A medium-sized hunting dog known for its endurance, strength, and loyalty.",
    "entlebucher": "A small herding dog from Switzerland, known for its agility and versatility.",
    "eskimo": "Refers to the American Eskimo Dog, a small to medium-sized breed known for its intelligence and playful nature.",
    "finnish":  "A medium-sized herding dog known for its friendly and gentle nature.",
    "frise": "A small breed known for its cheerful and affectionate personality.",
    "gaddi": "A livestock guardian dog from India, known for its strength and protective nature.",
    "germanshepherd": "A large and versatile breed known for its intelligence, loyalty, and working ability.",
    "greyhound": "Refers to the Mudhol Hound, known for its speed and hunting ability.",
    "groenendael": "A Belgian Shepherd Dog known for its intelligence, agility, and versatility.",
    "havanese": "A small breed known for its friendly and playful nature.",
    "hound": "A large sighthound known for its elegance and independent nature.",
    "husky": "A medium-sized working dog known for its endurance, strength, and friendly nature.",
    "keeshond": "A medium-sized breed known for its friendly and outgoing personality.",
    "kelpie": "An intelligent and energetic herding dog known for its work ethic.",
    "kombai": "A powerful and protective breed from India, known for its loyalty and guarding ability.",
    "komondor": "A large livestock guardian dog known for its distinctive corded coat and protective nature.",
    "kuvasz": "A large livestock guardian dog known for its strength, intelligence, and protective nature.",
    "labradoodle": "A crossbreed between a Labrador Retriever and a Poodle, known for its friendly and intelligent personality.",
    "labrador": "A medium to large breed known for its friendly, outgoing, and versatile nature.",
    "leonberg": "A large and gentle breed known for its friendly and calm demeanor.",
    "lhasa": "Refers to the Lhasa Apso, a small breed known for its independent and loyal nature.",
    "malamute": "A large and powerful sled dog known for its endurance, strength, and friendly nature.",
    "malinois": "A Belgian Shepherd Dog known for its intelligence, agility, and working ability.",
    "maltese": "A small breed known for its playful and affectionate personality.",
    "mastiff": "A large and powerful breed known for its strength and protective nature.",
    "mexicanhairless": "A hairless breed known for its loyal and affectionate nature.",
    "mix": "Refers to mixed breed dogs, which can have a wide range of appearances and temperaments.",
    "mountain":  "A large and friendly breed known for its gentle and calm nature.",
    "mudhol": "Also known as the Caravan Hound, known for its speed and hunting ability.",
    "newfoundland": "A large and gentle breed known for its strength, calm demeanor, and swimming ability.",
    "otterhound": "A large scent hound known for its distinctive appearance and hunting ability.",
    "ovcharka": "A large and powerful livestock guardian dog known for its protective nature.",
    "papillon": "A small breed known for its distinctive butterfly-like ears and friendly nature.",
    "pariah":  "Refers to the Indian Pariah Dog, known for its adaptability and intelligence.",
    "pekinese": "A small breed known for its distinctive appearance and independent nature.",
    "pembroke": "Refers to the Pembroke Welsh Corgi, known for its intelligence and friendly nature.",
    "pinscher":  "A small and energetic breed known for its fearless and lively personality.",
    "pitbull": "A medium-sized breed known for its strength, loyalty, and affectionate nature.",
    "pointer":"A versatile hunting dog known for its intelligence and athleticism.",
    "pomeranian": "A small breed known for its fluffy coat and lively personality.",
    "poodle": "A versatile and intelligent breed known for its friendly and trainable nature.",
    "pug": "A small breed known for its distinctive wrinkled face and playful personality.",
    "puggle": "A crossbreed between a Pug and a Beagle, known for its friendly and playful nature.",
    "pyrenees": "Refers to the Great Pyrenees, a large and gentle livestock guardian dog.",
    "rajapalayam":  "A large and powerful breed from India, known for its guarding ability and loyalty.",
    "redbone": "Refers to the Redbone Coonhound, known for its hunting ability and friendly nature.",
    "retriever": "A large and versatile hunting dog known for its strength and endurance.",
    "ridgeback": "A large and powerful breed known for its distinctive ridge of hair along its back and hunting ability.",
    "rottweiler": "A large and powerful breed known for its strength, loyalty, and protective nature.",
    "saluki": "A medium-sized sighthound known for its speed, endurance, and gentle nature.",
    "samoyed": "A medium-sized working dog known for its friendly and outgoing personality.",
    "schipperke": "A small breed known for its lively and curious nature.",
    "schnauzer":  "A large and powerful breed known for its intelligence and protective nature.",
    "segugio": "A scent hound breed known for its hunting ability and friendly nature.",
    "setter": "A medium to large breed known for its friendly and gentle nature.",
    "sharpei": "A medium-sized breed known for its distinctive wrinkled skin and independent nature.",
    "sheepdog": "A large and shaggy herding dog known for its gentle and protective nature.",
    "shiba": "A small and agile breed from Japan, known for its spirited and independent nature.",
    "shihtzu": "A small breed known for its distinctive appearance and friendly nature.",
    "spaniel": "Refers to the Cavalier King Charles Spaniel, known for its friendly and affectionate nature.",
    "spitz": "Refers to the Indian Spitz, known for its friendly and playful nature.",
    "springer": "A medium-sized hunting dog known for its friendly and energetic personality.",
    "stbernard": "A large and gentle breed known for its strength and calm demeanor.",
    "terrier":  "Refers to the American Pit Bull Terrier, known for its strength and loyalty.",
    "tervuren": "A Belgian Shepherd Dog known for its intelligence, agility, and versatility.",
    "vizsla": "A medium-sized hunting dog known for its friendly and energetic personality.",
    "waterdog": "A medium-sized breed known for its distinctive curly coat and agility.",
    "weimaraner": "A large and athletic breed known for its intelligence, energy, and versatility.",
    "whippet": "A medium-sized sighthound known for its speed, agility, and gentle nature.",
    "wolfhound": "A large and gentle breed known for its strength, speed, and calm demeanor."

}


def fetch_dog_breeds():
    response = requests.get(DOG_API_URL)
    if response.status_code == 200:
        breeds_data = response.json()
        breeds = list(breeds_data['message'].keys())
        return breeds
    else:
        return []


def fetch_breed_image(breed):
    response = requests.get(DOG_IMAGE_API_URL.format(breed=breed))
    if response.status_code == 200:
        image_data = response.json()
        return image_data['message']
    else:
        return None


def fetch_breed_description(breed):
    return BREED_DESCRIPTIONS.get(breed.lower(), "No description available")


def get_dog_breeds():
    breeds = list(breeds_collection.find({}, {"_id": 0, "breed": 1}))
    if not breeds:
        breeds_list = fetch_dog_breeds()
        if breeds_list:
            breeds_collection.insert_many([{"breed": breed} for breed in breeds_list])
        breeds = list(breeds_collection.find({}, {"_id": 0, "breed": 1}))
    return [breed['breed'] for breed in breeds]


def get_breed_info(breed):
    breed_info = images_collection.find_one({"breed": breed}, {"_id": 0})
    if not breed_info:
        image_url = fetch_breed_image(breed)
        description = fetch_breed_description(breed)
        if image_url:
            breed_info = {"breed": breed, "image_url": image_url, "description": description}
            images_collection.insert_one(breed_info)
    else:
        breed_info["description"] = fetch_breed_description(breed)
    return breed_info


def get_climate_data(location):
    params = {"key": WEATHER_API_KEY, "q": location}
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError as e:
            print(f"JSON decoding failed: {e}")
            return None
    else:
        return None


class SuggestBreedView(APIView):
    def get(self, request):
        location = request.GET.get('location')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 25))

        if not location:
            return Response({"error": "Location parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        climate_data = get_climate_data(location)
        if not climate_data:
            return Response({"error": "Could not retrieve climate data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        temperature = climate_data['current']['temp_c']
        if temperature < 10:
            climate_type = "cold"
        elif temperature > 25:
            climate_type = "warm"
        else:
            climate_type = "temperate"

        breeds = get_dog_breeds()

        suitable_breeds = [breed for breed in breeds if climate_type in ["temperate", "warm", "cold"]]

        breeds_with_info = []
        for breed in suitable_breeds:
            breed_info = get_breed_info(breed)
            breeds_with_info.append(breed_info)

        paginator = Paginator(breeds_with_info, limit)
        page_obj = paginator.get_page(page)

        return Response({
            "location": location,
            "current_page": page,
            "total_pages": paginator.num_pages,
            "total_breeds": paginator.count,
            "suitable_breeds": list(page_obj)
        }, status=status.HTTP_200_OK)



# @csrf_exempt
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# def create_pet(pet_data):
#     serializer = PetSerializer(data=pet_data)
#     if serializer.is_valid():
#         pet = serializer.save()
#         print(pet)
#         return pet
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddFavoritePetView(APIView):
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        breed = request.data.get('breed')
        if not breed:
            return Response({'error': 'Missing breed in request data'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = Pet.objects.get(breed=breed)  # Use MongoEngine's get with pk

        except DoesNotExist:
            print("Pet does not exist")
            pet_data = request.data.copy()  # Avoid modifying original request data
            serializer = PetSerializer(data=pet_data)
            if serializer.is_valid():
                print("new Pet data validated")
                pet = serializer.save()  # Save the pet first
                print(pet)
                # print(serializer.data)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = UserProfile.objects.get(user=user)
        except DoesNotExist:
            profile = UserProfile(user=user)

        # if not isinstance(pet, Pet):
        #     return pet

        profile.favorite_pets.append(pet)
        profile.save()
        return Response({"message": "Pet added to favorites"}, status=status.HTTP_200_OK)


class RemoveFavoritePetView(APIView):
    pass


class GetFavoritePetsView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_profile = UserProfile.objects.get(user=user)
        except DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

        pets = user_profile.favorite_pets

        print(pets)

        # Serialize the list of favorite pets
        pet_list = PetSerializer(pets, many=True).data

        return Response(pet_list, status=status.HTTP_200_OK)

