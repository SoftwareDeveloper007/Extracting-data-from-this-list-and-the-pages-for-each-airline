from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import unittest, csv

class mainScraper_test(unittest.TestCase):

    def setUp(self):

        ''' Initialize Parameters'''
        self.start_url = "https://www.flightradar24.com/data/aircraft/"
        self.output_data = []
        self.links = []

        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def Scraping_test(self):

        ''' 1. Navigate to a start url '''
        pTxt = "\n1. Navigate to a start url: {}\n".format(self.start_url)
        print(pTxt)

        try:
            self.driver.get(self.start_url)
            pTxt = "\t\t(Success)\tLoad webpage successfully"
            print(pTxt)
        except:
            pTxt = "\t\t(Failure)\tFailed to load webpage"
            print(pTxt)
            return

        ''' 2. Scraping main page '''
        pTxt = "2. Scraping main page"
        print(pTxt)

        temp_data = []
        try:
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table#tbl-datatable > tbody"))
            )
            rows = table.find_elements_by_tag_name("tr")

            j = 0
            for i, row in enumerate(rows):
                if i is 0 or row.get_attribute("class") is "header":
                    continue
                cols = self.driver.find_elements_by_tag_name("td")
                airline_name = cols[2].text.strip()
                airline_code = cols[3].text.strip()
                link = "https://www.flightradar24.com/data/aircraft" + cols[2].find_element_by_tag_name("a").get_attribute("href")
                temp_data.append({
                    "airline_name": airline_name,
                    "airline_code": airline_code,
                    "link": link
                })

                pTxt = "\t\tNo:\t\t{0}\nairline name:\t{1}\nairline code:\t{2}\nlink:\t{}\n".format(j, airline_name, airline_code, link)
                print(pTxt)
                j += 1

            pTxt = "\t\t(Success)\tExtracted table successfully"
            print(pTxt)
        except:
            pTxt = "\t\t(Failure)\tCan't extract table"
            print(pTxt)
            return

        ''' 3. Scraping sub pages '''
        pTxt = "3. Scraping sub pages"
        print(pTxt)

        cnt = 0
        for i, row in enumerate(temp_data):
            self.driver.get(row["link"])

            lies = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.horizontal-slide > li"))
            )

            for j, li in enumerate(lies):
                aircraft_type = li.find_element_by_css_selector("div > div").text.strip()
                aircraft_type = aircraft_type.replace(li.find_element_by_css_selector("div > div > span").text.strip(), "")

                sub_rows = li.find_elements_by_css_selector("ul > li")

                for k, sub_row in enumerate(sub_rows):
                    self.output_data.append({
                        "airline_name": row["airline_name"],
                        "airline_code": row["airline_code"],
                        "aircraft_type": aircraft_type,
                        "aircraft_registration": sub_row.text.strip()
                    })

                    pTxt = "\t\tNo:\t\t{0}\nairline name:\t{1}\nairline code:\t{2}\naircraft type:\t{3}\naircraft reg:\t{4}\n"\
                        .format(cnt, row["airline_name"], row["airline_code"], aircraft_type, sub_row.text.strip())
                    print(pTxt)
                    cnt += 1

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

        ''' 4. Save all data in a csv format '''
        pTxt = "4. Save all data in a csv format"
        print(pTxt)

        output_file = open("result.csv", 'w', encoding='utf-8', newline='')
        writer = csv.writer(output_file)

        header = ["airline name", "airline code", "aircraft type", "aircraft registration"]
        writer.writerow(header)

        for i, row in enumerate(self.output_data):
            writer.writerow([
                row["airline_name"],
                row["airline_code"],
                row["aircraft_type"],
                row["aircraft_registration"]
            ])

        output_file.close()

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(mainScraper_test)
    unittest.TextTestRunner(verbosity=2).run(suite)