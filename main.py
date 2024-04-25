import decryption
import os

from bot import bot
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()

    Matrixine = bot.Matrixine()
    Matrixine.run(token=os.getenv("UNSAFE_TOKEN"))
