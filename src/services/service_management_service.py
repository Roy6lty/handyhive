import json
from src.models import services_model


def get_all_services():
    with open("services3.json", "r") as file:
        data = json.load(file)
    return services_model.AllCategory(category=data)
