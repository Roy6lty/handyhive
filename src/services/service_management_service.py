import json
from src.models import service_provider_model


def get_all_services():
    with open("services2.json", "r") as file:
        data = json.load(file)
    return service_provider_model.AllCategory(category=data)
