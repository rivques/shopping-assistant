import dotenv
dotenv.load_dotenv(override=True)

import requests
import os
import bs4
import openai
import pyttsx3

oai_client = openai.Client(api_key=os.getenv('OPENAI_KEY'), base_url=os.getenv('OPENAI_BASE_URL'))
system_prompt = "You are an assistant to a visually impaired person. You are given images of products and should describe them in as much detail as possible. When possible, describe the actual product in addition to any claims the packaging might make. Use plain text and avoid Markdown formatting."

engine = pyttsx3.init()
engine.setProperty('rate', 300) 

def describe_upc(upc):
    # step one: look up the product by UPC with a custom google search
    search_url = f"https://www.googleapis.com/customsearch/v1?q=UPC%3A%20{upc}&key={os.getenv('SEARCH_API_KEY')}&siteSearch=target.com&siteSearchFilter=i&cx=e2d91e113b89b446b"
    print(f"Searching for UPC {upc} via URL {search_url}")
    search_response = requests.get(search_url)
    print(search_response.json())
    search_response.raise_for_status()
    result_page = search_response.json()['items'][0]['link']
    # step two: extract the product name and photo from the result
    product_page = requests.get(result_page)
    product_page.raise_for_status()
    print(product_page.text)
    product_soup = bs4.BeautifulSoup(product_page.text, 'html.parser')
    product_name = product_soup.select_one("#pdp-product-title-id").text
    print(f"Product name: {product_name}")
    # product_price = product_soup.select_one("[data-test=\"product-price\"]").text
    # print(f"Product price: {product_price}")
    product_image_els = product_soup.select("section[aria-label=\"Image gallery\"] img")
    print(f"Found {len(product_image_els)} images")
    product_image_urls = []
    for el in product_image_els:
        try:
            product_image_urls.append(el['src'])
        except KeyError:
            pass
    print(f"Image URLs: {product_image_urls}")
    message_content = [{"type": "text", "text": f"Describe this product. Name: {product_name}"}]
    for url in product_image_urls:
        message_content.append({"type": "image_url", "image_url": {"url": url, "detail": "low"}})
    # step three: throw it at gpt4omini
    oai_response = oai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message_content}
        ]
    )
    print(oai_response)
    print()
    print(oai_response.choices[0].message.content)
    # step four: text-to-speecch the result
    engine.say(oai_response.choices[0].message.content)
    engine.runAndWait()

if __name__ == "__main__":
    while True:
        upc = input("Enter a UPC: ")
        describe_upc(upc)