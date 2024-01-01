# FS-HairstyleScraping

Automating Scraping and Cleaning of images. It then creates a simple GUI to show to the user for accepting or rejecting cleaned images

## Description of the Process

- Scrapes Images from supplied queries
- Cleans images based on quality, faces found count and face angle
- Shows the cleaned images to the user to accept or reject


## Launching Programing

**Directions**

- Put all the styles that want to be scraped into the `styles.txt` file
    - These are the queries that will be search in google images
- Run the below command to launch the program
```cmd
python Launch.py
``` 


## Tools

**Previewing a query**

- Open `tools/openquery.py` and change the `query="wanted query"`. Then run the below script to open the page in the browser.
```cmd
python tools/openquery.py
```



