import requests
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

url = "https://www.bbc.com"

try:
    response = requests.get(url, timeout=10)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    raw_headlines = soup.find_all("h2")
    headlines = []

    for h in raw_headlines:
        text = h.get_text(strip=True)
        if text and text not in headlines:
            headlines.append(text)

    if not headlines:
        print(Fore.RED + "⚠ No headlines found — site structure may have changed.")
    else:
        try:
            count = int(input("How many headlines do you want? "))
        except ValueError:
            count = 10

        print(Fore.YELLOW + "\nLatest Headlines:\n" + Style.RESET_ALL)
        for i, headline in enumerate(headlines[:count], start=1):
            print(Fore.CYAN + f"{i}. " + Style.RESET_ALL + headline)

        filename = f"headlines_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            for headline in headlines[:count]:
                file.write(headline + "\n")

        print(Fore.GREEN + f"\n Headlines saved to '{filename}'")

except requests.RequestException as e:
    print(Fore.RED + f" Network error: {e}")

