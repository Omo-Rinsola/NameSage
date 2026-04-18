# External API calls that talks to Genderize, Agify, Nationalize APIs
import httpx


async def get_gender_data(name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.genderize.io?name={name}")
        return response.json()


async def get_age_data(name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.agify.io?name={name}")
        return response.json()


async def get_country_data(name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.nationalize.io?name={name}")
        return response.json()

