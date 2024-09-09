import requests
import os
import bs4
import openai
import subprocess

oai_client = openai.Client(api_key=os.getenv('OPENAI_KEY'), base_url=os.getenv('OPENAI_BASE_URL'))
system_prompt = "You are an assistant to a visually impaired person. You are given images of products and should describe them in as much detail as possible. When possible, describe the actual product in addition to any claims the packaging might make. Use plain text and avoid Markdown formatting."

# engine = pyttsx3.init()
# engine.setProperty('rate', 300) 

def get_product_page_url_target(upc):
    # step one: look up the product by UPC with a custom google search
    search_url = f"https://www.googleapis.com/customsearch/v1?q=UPC%3A%20{upc}&key={os.getenv('SEARCH_API_KEY')}&siteSearch=target.com&siteSearchFilter=i&cx=e2d91e113b89b446b"
    print(f"Searching for UPC {upc} via URL {search_url}")
    search_response = requests.get(search_url)
    print(search_response.json())
    search_response.raise_for_status()
    return search_response.json()['items'][0]['link']

def get_message_content_target(result_page_url):
    # step two: extract the product name and photo from the result
    product_page = requests.get(result_page_url)
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
    return message_content

def get_text_description(message_content):
    oai_response = oai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message_content}
        ]
    )
    print(oai_response)
    print()
    return oai_response.choices[0].message.content

def describe_upc(upc):
    result_page_url = get_product_page_url_target(upc)
    message_content = get_message_content_target(result_page_url)
    # step three: throw it at gpt4omini
    text_description = get_text_description(message_content)
    # step four: text-to-speecch the result
    return text_description

def text_to_wav(text, filepath):
    subprocess.run(["espeak", "-w", filepath, text])

def wav_to_mp3(wavpath, mp3path):
    subprocess.run(["ffmpeg", "-y", "-i", wavpath, mp3path])

if __name__ == "__main__":
    while True:
        upc = input("Enter a UPC: ")
        describe_upc(upc)