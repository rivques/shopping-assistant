import requests
import os
import bs4
import openai
import subprocess
import wave
import numpy as np
from nix.models.TTS import NixTTSInference


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

nix = NixTTSInference(model_dir = "ttsmodel")

def text_to_wav(text, filepath):
    wavless_path = filepath[:-4]
    # split into sentences, synthesize, then concatenate the wav files
    partial_files = []
    sentences = split_text_into_sentences(text)
    for i, sentence in enumerate(sentences):
        print(f"Synthesizing sentence {i}: {sentence}")
        one_text_to_wav(sentence, f"{wavless_path}_{i}.wav")
        partial_files.append(f"{wavless_path}_{i}.wav")    
    cmd_to_run = ["sox"] + partial_files + [filepath]
    print(f"Concatenating {len(sentences)} wav files into {filepath} with command {cmd_to_run}")
    subprocess.run(cmd_to_run)
    for i in range(len(sentences)):
        os.remove(f"{wavless_path}_{i}.wav")

def split_text_into_sentences(text):
    # split on sentence or newline
    # trim leading or trailing whitespace
    # retain punctuation
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    sentences = []
    for line in lines:
        sentences += [sentence.strip() + "." for sentence in line.split(".") if sentence.strip()]
    return sentences

def one_text_to_wav(text, filepath):
    # tokenization
    c, c_length, phoneme = nix.tokenize(text)
    # Convert text to raw speech
    xw = nix.vocalize(c, c_length)
    # Save the speech to a wav file
    write_wav(xw, filepath)

def write_wav(xw, filepath):
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(22050)
        wav_file.writeframes((2 ** 15 * xw).astype(np.int16).tobytes())

def wav_to_mp3(wavpath, mp3path):
    subprocess.run(["ffmpeg", "-y", "-i", wavpath, "-filter:a", "atempo=1.5", mp3path])

if __name__ == "__main__":
    while True:
        upc = input("Enter a UPC: ")
        describe_upc(upc)