#!/usr/bin/env python
#-*- coding:UTF-8 -*-

#rikujjs


from bs4 import BeautifulSoup
import requests
from time import sleep

#column_headers array contains the names for the columns.
column_headers = ["Brand", "Model", "Release", "Clockrate", "Cores", "Cache","FSB", "Socket"]


months_dict = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}


class Scraper:

    #make the parsed soup in to a variable called "soup"
    def __init__(self, url, year, output):

        self.url = url
        self.year = year
        self.write_handle = output

        #initialize the datastorage[] dict
        for header in column_headers:
            self.datastorage[header] = '-'

        #include possible spoofed header, and get the page
        header = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=header)

        #make some soup
        self.soup = BeautifulSoup(r.text.encode('utf-8', 'ignore'))

    #we go thru the datastorage[] dict and write the info to a string, separated with ';'
    def info_to_string(self):

        info_string = ""

        #write the columns to a single string, place a ';' in between
        for header in column_headers:

            info_string += ';'
            info_string += self.datastorage[header].strip().encode('utf-8', 'ignore').replace(";", '')


        #get rid of the first ;
        info_string = info_string.replace(";", "", 1)

        return info_string

    #format the date to a more usable form, eg. 2-2005
    def get_date(self, month):

        try:
            month_number = months_dict[month]
        except KeyError:
            print self.url
            return self.year

        return str(month_number)+'-'+self.year

    def get_months_models(self, data, brand, date):


        self.datastorage["Brand"] = brand
        self.datastorage["Release"] = self.get_date(date)

        models = data.findAll('a')
        specs = data.findAll("div", "pad1 even_smaller")

        #remove the first one since theres a extra element which doesnt contain anything useful
        if brand == "AMD":
            del models[0]


        for x in range(0, 50):


            try:

                #make sure the dict is empty
                for key in self.datastorage:
                    self.datastorage[key] = '-'

                #brand and release
                self.datastorage["Brand"] = brand
                self.datastorage["Release"] = self.get_date(date)


                self.datastorage["Model"] = models[x].text
                specs_split = specs[x].text.split('/')

                for spec in specs_split:

                    if "Hz" in spec:
                        self.datastorage["Clockrate"] = spec.strip()
                    elif "core" in spec.lower():
                        self.datastorage["Cores"] = spec.strip()
                    elif "socket" in spec.lower():
                        self.datastorage["Socket"] = spec.strip()
                    elif "fsb" in spec.lower():
                        self.datastorage["FSB"] = spec.strip()
                    elif "l1" in spec.lower() or "l2" in spec.lower() or "l3" in spec.lower() or "l4" in spec.lower():
                        self.datastorage["Cache"] = spec.strip()
                    else:
                        print spec
                        print self.url


                #place the model info into a string, and store in a array for later use
                model_specs = self.info_to_string()
                self.page_data.append(model_specs)


                #self.write_handle(model_specs)
                #self.write_handle('\n')
            except IndexError:
                pass


    #do the actual scraping
    def get_pageinfo(self):

        #do the actual scraping here
        info = self.soup.find("div", "p_div")
        monthly_info = info.findAll("tr")

        for month_info in monthly_info:
            info_line = month_info.findAll('td')

            if month_info.find("th") is not None:
                continue

            if len(info_line) > 0 and info_line[0] is not None:

                try:
                    self.get_months_models(info_line[1], "AMD", info_line[0].text)
                except:
                    #this month didnt have amd launches
                    print "no amd this month"
                try:
                    self.get_months_models(info_line[2], "Intel", info_line[0].text)
                except:
                    print "no intels"


        #eventualy return the collected data
        return self.page_data

    #member variables
    soup = None
    datastorage = {}
    year = None
    url = None
    write_handle = None
    page_data = []

if __name__ == "__main__":



    #modifie the starting id if you need the restart the program from a different location. eg. after a crash
    starting_id = '2004'


    #insert the base of the url's we're going to scrape
    baseurl = "http://www.cpu-world.com/Releases/Desktop_CPU_releases_({0}).html".format(starting_id)


    #the file we are gonna write the gotten info, the file has the starting_id in it, in case starting
    #from somewhere else than the begining.
    output_file = "cpu-world{0}.csv".format(starting_id)
    output = open(output_file, 'w')

    #loop the games from starting_id to end.
    for i in range(0, 11):

        baseurl = "http://www.cpu-world.com/Releases/Desktop_CPU_releases_({0}).html".format(starting_id)

        print baseurl


        #get the page, BS it, and get the pageinfo
        page_to_get = Scraper(baseurl, starting_id, output)
        page_info = page_to_get.get_pageinfo()

        for page in page_info:
            output.write(page)
            output.write('\n')

        #be nice
        sleep(3)

        next_year = int(starting_id)+1
        starting_id = str(next_year)












