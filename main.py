import decryption

from bot import bot
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()

    Matrixine = bot.Matrixine(decryption.DecryptMatrixineToken())
    Matrixine.run()
