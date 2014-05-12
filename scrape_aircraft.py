import requests
from bs4 import BeautifulSoup
import csv
from unidecode import unidecode

# Create a list of the plane models, their respective URL chunks, and their respective page counts.

# Initialize empty list for holding the tuples.
planes = []

# Go to the 'main' page.
url = "http://www.airfleets.net/recherche/supported-plane.htm"
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')

for td in soup.find_all('td', attrs = {'class': 'tdtexten'}):
    # Get model name and URL chunk from main page.
    model = td.a.string
    url_chunk = td.a.get('href').split('listing/')[1].split('-1')[0]

    # Go to first page for the current model.
    url = "http://www.airfleets.net/listing/%s-1.htm" % url_chunk
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    # Find the page count.
    a = soup.find('a', attrs = {'class': 'page2'})
    pages = int(a.string.split('/')[1])

    # Append tuple to the planes list.
    planes.append((model, url_chunk, pages))

# Open CSV file for writing.
with open('aircraft_raw.csv', 'wb') as file:
    writer = csv.writer(file, delimiter = ',', quotechar = '"')
    # Create header row.
    writer.writerow(["msn", "model", "series", "airline", "ff_day", "ff_month", "ff_year", "registration", "status"]) # ff = first flight

    for model, url_chunk, max_pages in planes:
        # Loop through each page for the current model.
        for page in range(1, max_pages + 1):
            url = "http://www.airfleets.net/listing/%s-%s.htm" % (url_chunk, str(page))
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'lxml')

            # Loop through each row of the table on the current page.
            for tr in soup.find_all('tr', attrs = {'class': 'trtab'}):
                try:
                    # Some models have an extra "LN" column, so I need to use different indices when going through the columns.
                    if (url_chunk == 'dc10' or url_chunk == 'md11' or url_chunk == 'md80' or url_chunk == 'bae146' or url_chunk.find('b7') != -1):
                        msn = tr.contents[1].a.string

                        if(tr.contents[5].string != None):
                            series = tr.contents[5].string.replace('\n', '').strip()
                        else:
                            series = None

                        if(tr.contents[7].a.string != None):
                            airline = unidecode(tr.contents[7].a.string)
                        else:
                            airline = None

                        if(tr.contents[9].string != None):
                            ff = tr.contents[9].string.replace(' ', '').replace('\n', '').replace(u'\xa0', '')
                        else:
                            ff = None

                        registration = tr.contents[11].a.string

                        if(tr.contents[13].string != None):
                            status = tr.contents[13].string.replace('\n', '').strip()
                        else:
                            status = None

                    # Some pages do not have an "LN" column, so I need to use different indices when going through the columns.
                    else:
                        msn = tr.contents[1].a.string

                        if(tr.contents[3].string != None):
                            series = tr.contents[3].string.replace('\n', '').strip()
                        else:
                            series = None

                        if(tr.contents[5].a.string != None):
                            airline = unidecode(tr.contents[5].a.string)
                        else:
                            airline = None

                        if(tr.contents[7].string != None):
                            ff = tr.contents[7].string.replace(' ', '').replace('\n', '').replace(u'\xa0', '')
                        else:
                            ff = None

                        registration = tr.contents[9].a.string

                        if(tr.contents[11].string != None):
                            status = tr.contents[11].string.replace('\n', '').strip()
                        else:
                            status = None

                    # Split date into day, month, year.
                    if(ff != None):
                        s = ff.split('/')
                        if (len(s) == 3):           # 'DD/MM/YYYY'
                            ff_day = int(s[0])
                            ff_month = int(s[1])
                            ff_year = int(s[2])
                        elif (len(s) == 2):         # 'MM/YYYY'
                            ff_day = None
                            ff_month = int(s[0])
                            ff_year = int(s[1])
                        elif (len(s) == 4):         # 'YYYY'
                            ff_day = None
                            ff_month = None
                            ff_year = s
                        else:                       # Empty.
                            ff_day = None
                            ff_month = None
                            ff_year = None
                    else:
                        ff_day = None
                        ff_month = None
                        ff_year = None

                    # Write data to new row in CSV.
                    writer.writerow([msn, model, series, airline, ff_day, ff_month, ff_year, registration, status])

                # Add exception for troubleshooting purposes.
                except Exception:
                    print("There was an error with a/an %s observation on page %s." % (model, str(page)))
                    print(tr.contents)
                    pass