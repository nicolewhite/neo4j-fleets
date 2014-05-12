import requests
import csv
from bs4 import BeautifulSoup
import string
from unidecode import unidecode
import warnings
warnings.simplefilter("ignore", RuntimeWarning) # unidecode doesn't like anything I'm doing.

# Create a list of letters a through z.
letters = list(string.lowercase)

# Initialize empty list for holding the page counts.
pages = []

for letter in letters:
    # Go to the first page for the current letter.
    url = "http://www.airfleets.net/recherche/list-airline-%s_0.htm" % letter
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    # Find how many pages there are for the current letter.
    a = soup.find('a', attrs = {'class': 'page2'})
    p = int(a.string.split('/')[1])

    # Append page count to pages array.
    pages.append(p)

# Create a list of tuples (letter, page).
letters_pages = zip(letters, pages)

# Open CSV for data write.
with open('airlines_raw.csv', 'wb') as file:
    writer = csv.writer(file, delimiter = ',', quotechar = '"')
    # Create header row.
    writer.writerow(["airline", "country", "status"])

    for letter, max_page in letters_pages:
        for i in range(1, max_page + 1):
            url = "http://www.airfleets.net/recherche/list-airline-%s_%s.htm" % (letter, str((i - 1) * 20)) # Number in URL is in increments of 20.
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'lxml')

            for tr in soup.find_all('tr', attrs = {'class': 'trtab'}):
                try:
                    airline = unidecode(tr.contents[1].a.string)
                    country = unidecode(str(tr.contents[3]).split('>  ')[1].replace('</td>', ''))
                    if(str(tr.contents[5]).find('inactive') != -1):
                        status = 'Inactive'
                    else:
                        status = 'Active'

                    # Add data to CSV.
                    writer.writerow([airline, country, status])

                # Add exception for troubleshooting purposes.
                except Exception:
                    print("There was an error on page %s for letter %s") % (str(i), letter)
                    print(tr.contents)
                    pass