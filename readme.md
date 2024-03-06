# JLPT SCRAPPER

Scrap over the JLPT-Sensei Website in a Anki readable CSV

## Installation

```powershell
conda create --name jlpt-scrapper
conda activate jlpt-scrapper
```

Multiple libraries are needed, using pip
```powershell
pip install requests beautifulsoup4 deepl alive-progress
```

## Launch

```powershell
python ./scrapper.py
```

Multiple parameters will be asked :
- Do you want to use Deepl to translate the grammar automatically from english to french ?
  
    It will use the deeplApi to automatically translate all the sentences from the meaning to the examples in french. But it requires a deeplApi account key (which is free)
    - yes : paste the deepl Api key, will translate
    - no :  will not translate
- Enter the JLPT level to scrape (N1, N2, N3, N4, N5): 
Each level can be scrapped, it will create a different output csv

## How to transfer in Anki ?
1) Import the [Anki package](GrammarWithExample.apkg) in Anki (File->Import) so that the new Card Type "Grammaire avec exemples" is created
2) You can already delete this deck
3) Import the csv file output by the python that way
    ![alt text](readmeImages/image.png)
    Make sure to select "virgule" and the HTML box
    ![alt text](readmeImages/image2.png)
    Make sure everything is aligned, it should be automatic