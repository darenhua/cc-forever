

from services.claude import generate
from dotenv import load_dotenv

load_dotenv()

filename = generate("goku", "Create an image of goku with a pure white background.", "#ffffff")


