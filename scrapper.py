import requests
import deepl
from bs4 import BeautifulSoup
import csv
import os
from alive_progress import alive_bar


def scrape_jlpt_page(page_number, jlpt_level):
    if page_number == 1:
        url = f"https://jlptsensei.com/jlpt-n{jlpt_level}-grammar-list/"
    else:
        url = f"https://jlptsensei.com/jlpt-n{jlpt_level}-grammar-list/page/{page_number}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    grammar_list = []

    for tr in soup.select("div.full-mobile.table-responsive table#jl-grammar tbody tr"):
        link = tr.select_one("td.jl-td-gr a")
        if link is None:
            continue
        href = link["href"]
        grammar_list.append(href)

    return grammar_list


def scrape_jlpt_grammar(link, translator: deepl.Translator):
    response = requests.get(link)
    if response.status_code != 200:
        print(f"Failed to scrape {link}")
        return link, None, None, None, [("N/A", "N/A", "N/A") for _ in range(10)]
    soup = BeautifulSoup(response.text, "html.parser")
    japanese_meaning = soup.select_one("span.jp")
    if japanese_meaning is None:
        print(f"Failed to scrape {link}")
        return link, None, None, None, [("N/A", "N/A", "N/A") for _ in range(10)]
    japanese_meaning = japanese_meaning.text.strip()
    english_meaning = soup.select_one("p.eng-definition").text.strip()
    french_meaning = "N/A"
    if translator is not None:
        french_meaning = translator.translate_text(
            english_meaning, source_lang="EN", target_lang="FR"
        )

    image_url = soup.select_one("img#header-image")["src"]
    image_alt = soup.select_one("img#header-image")["alt"]
    image_name = f"{image_alt}.png"
    image_path = f"images/{image_name}"

    # Download image
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists(image_path):
        with open(image_path, "wb") as f:
            f.write(requests.get(image_url).content)

    examples = []
    for i in range(1, 11):
        example_div = soup.select_one(f"div#example_{i}")
        if example_div:
            japanese_example = "".join(
                example_div.select_one("p.m-0.jp").stripped_strings
            )
            english_example = example_div.select_one(
                "div.alert.alert-primary"
            ).text.strip()
            if translator is not None:
                french_example = translator.translate_text(
                    english_example, source_lang="EN", target_lang="FR"
                )
                examples.append((japanese_example, english_example, french_example))
            else:
                examples.append((japanese_example, english_example, "N/A"))
        else:
            examples.append(("N/A", "N/A", "N/A"))

    return japanese_meaning, english_meaning, french_meaning, image_name, examples


def save_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        row = [
            "Japanese grammar",
            "English Meaning",
            "French Meaning",
            "link of the image",
        ]
        for i in range(1, 11):
            row.append(f"example {i} jp")
            row.append(f"example {i} eng")
            row.append(f"example {i} fr")
        writer.writerow(row)
        for row in data:
            row[3] = f"<img src='{row[3]}'>"
            writer.writerow(row)


def main():
    use_Deepl = input(
        "Do you want to use Deepl to translate the grammar automatically from english to french ? (yes/no): "
    )
    if use_Deepl == "yes":
        use_Deepl = True
    else:
        use_Deepl = False
    if use_Deepl:
        deepl_auth_key = input("Enter your Deepl API key: ")
        translator = deepl.Translator(deepl_auth_key)
    else:
        deepl_auth_key = None
        translator = None

    which_JLPT = input("Enter the JLPT level to scrape (N1, N2, N3, N4, N5): ")
    if which_JLPT == "N1":
        num_pages = 7
        jlpt = 1
    elif which_JLPT == "N2":
        num_pages = 5
        jlpt = 2
    elif which_JLPT == "N3":
        num_pages = 5
        jlpt = 3
    elif which_JLPT == "N4":
        num_pages = 4
        jlpt = 4
    elif which_JLPT == "N5":
        num_pages = 3
        jlpt = 5
    all_grammar_links = []
    grammar_data = []
    with alive_bar(
        total=num_pages,
        title="Scrapping Pages",
        bar="smooth",
        spinner="elements",
        dual_line=True,
    ) as bar:
        for page_number in range(1, num_pages + 1):
            bar.text(f"Scrapping Page {page_number} out of {num_pages}")
            grammar_links = scrape_jlpt_page(page_number, jlpt)
            all_grammar_links.extend(grammar_links)
            bar()
    y = 1
    with alive_bar(
        total=len(all_grammar_links),
        title="Scrapping Grammar Points",
        bar="smooth",
        spinner="elements",
        dual_line=True,
    ) as bar:
        for link in all_grammar_links:
            reduced_link = link.split("/")[-2]
            bar.text(f"Scrapping {reduced_link},   {y} out of {len(all_grammar_links)}")
            y += 1
            data = scrape_jlpt_grammar(link, translator)
            grammar_data.append(
                [data[0], data[1], data[2], data[3]]
                + [example for example_tuple in data[4] for example in example_tuple]
            )
            bar()

    filename = f"jlpt_n{jlpt}_grammar.csv"
    if os.path.exists(filename):
        os.remove(filename)
    save_to_csv(grammar_data, filename)
    print(f"Data saved to {filename}")


if __name__ == "__main__":
    main()
