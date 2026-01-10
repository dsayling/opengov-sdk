from httpx import Client
import os

COMMUNITY = "your-community"
LIST_RECORDS = f"https://api.plce.opengov.com/plce/v2/{COMMUNITY}/records"
API_KEY = os.getenv("OPENGOV_API_KEY")


def get_client() -> Client:
    return Client(headers={"Authorization": f"Token {API_KEY}"})


def list_records():
    with get_client() as client:
        response = client.get(LIST_RECORDS)
        return response.json()


def list_users():
    with get_client() as client:
        response = client.get(f"https://api.plce.opengov.com/plce/v2/{COMMUNITY}/users")
        return response.json()


if __name__ == "__main__":
    records = list_records()
    print(records)
