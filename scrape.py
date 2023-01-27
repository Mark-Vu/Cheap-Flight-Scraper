from time import sleep
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime


class Flight:
    def __init__(self):
        """
        Basic blueprint for a flight
        """
        self.price = "Price Unavailable"
        self.stop = "Stops Unavailable"
        self.depart_day = "Departure Days Unavailable"
        self.flight_duration = 'Duration Unavailable'
        self.layovers = 'Layovers Unavailable'
        self.airlines_code = 'Airlines Unavailable'

    def printRoundTripInfo(self):
        print(f'Departure day: {self.depart_day}')
        for i, key in enumerate(self.layovers):
            print(f'{self.flight_duration[i]} --> {self.layovers[key]} layovers at {key} --> {self.flight_duration[i+1]}')
        print(f'Airlines: ')
        for carrier in self.airlines_code:
            print(f'{carrier}')

    def printOneWayInfo(self):
        print(f"________________________________________________________________")
        print(f'Price: {self.price}')
        print(f'Departure Day: {self.depart_day}')
        print(f'Duration: {self.flight_duration}')
        print(f'Layovers: {self.layovers}')
        print("Airlines(s): ")
        print(f'{self.airlines_code}')
        print(f'{self.stop} stop(s)')

class OneWayFlight(Flight):
    def __init__(self):
        super().__init__()


class RoundTripFlight(Flight):
    def __init__(self):
        super().__init__()
        self.depart_flight = Flight()
        self.return_flight = Flight()

    def dataRoundTrip(self):
        print(f"_____________________________________________________________________________")
        print(f'price: {self.price}')
        print(f"Depart flight ticket: -----------------------------------")
        self.depart_flight.printRoundTripInfo()
        print(f"return flight ticket: -----------------------------------")
        self.return_flight.printRoundTripInfo()
        


class Scraper:
    """
    All scraping part will be in this Scraper class
    """
    def __init__(self, type, dest, depart, date_leave, date_return="NULL", seat_class="economy"):
        self.type = type
        self.dest = dest
        self.depart = depart
        self.date_leave = date_leave
        self.date_return = date_return
        self.seat_class = seat_class
        self.flights = []

        chrome_options = Options()
        # chrome_options.add_argument("--headless")

        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)

    def returnUrl(self):
        if self.type == "One Way":
            url = "https://www.google.com/travel/flights?q=Flights%20to%20{}%20from%20{}%20on%20{}%20one%20way%20{}"
            return url.format(self.dest, self.depart, self.date_leave, self.seat_class)
        else:
            """
            self.seat_class->str: ECONOMY, BUSINESS
            """
            url = "https://www.ca.kayak.com/flights/{}-{}/{}/{}/{}?sort=bestflight_a"
            self.date_leave = datetime.datetime.strptime(self.date_leave, "%m-%d-%Y").strftime("%Y-%m-%d")
            self.date_return = datetime.datetime.strptime(self.date_return, "%m-%d-%Y").strftime("%Y-%m-%d")

            return url.format(self.depart,
                              self.dest,
                              self.date_leave,
                              self.date_return,
                              self.seat_class)

    def scrape(self, obj, html_element):
        depart_day = html_element.find("span", {"class": "X3K_-header-text"}).text
        special = u"\u2022"
        depart_day = depart_day.replace(special, "")
        depart_day = " ".join(depart_day.split())
        obj.depart_day = depart_day
        
        layovers = html_element.find_all("div", {"class": "c62AT-layover-info"})
        layovers_list = {}      
        for layover in layovers:
            #Get the duration of layover text: hh mm and change it to hhmm
            layover_duration = layover.find("span", {"class": "c62AT-duration"}).text
            layover_duration = re.sub(r"\s", '', layover_duration)
            layover_airport = layover.find_all("span")[2].text
            layover_airport = layover_airport.replace(' (', '(').replace('Change planes in ', '')
            layovers_list[layover_airport] = layover_duration
        obj.layovers = layovers_list

        obj.stop = len(obj.layovers)
        carriers = html_element.find_all("div", {"class": "nAz5-carrier-text"})
        carrier_list = []
        for carrier in carriers:
            carrier_list.append(carrier.text)
        obj.airlines_code = carrier_list

        flight_times = html_element.find_all("span", {"class": "g16k-time"})
        flight_duration = []
        for time in flight_times:
            flight_duration.append(time.text)
        obj.flight_duration = flight_duration
        
    def scrapeRoundTrip(self):
        url = self.returnUrl()
        self.driver.get(url)
    
        sleep(10)
        flag = 0

        flights = self.driver.find_elements(By.XPATH, "//div[@class='nrc6']")
        buttons = self.driver.find_elements(By.XPATH, "//div[@class='nrc6-content-section']")

        if not flights:
            flag = 1
            flights = self.driver.find_elements(By.XPATH, "//div[@class='resultWrapper']")
            buttons = self.driver.find_elements(By.XPATH, "//div[@class='resultWrapper']")
        
        for button in buttons:
            button.click()
            sleep(0.5)
        sleep(2)
        for flight in flights:
            html_element = flight.get_attribute('outerHTML')
            soup = BeautifulSoup(html_element, "html.parser")

            new_flight = RoundTripFlight()
            
            if flag == 1:
                temp_price = soup.find("div", {"class": "col-price result-column js-no-dtog"})
                price = temp_price.find("span", {"class": "price-text"}).text
            else:
                price = soup.find("div", {"class": "f8F1"}).text
            new_flight.price = price

            
            #Get the html for seperately for departure flights and return flights
            depart_return_html = soup.find_all("div", {"class": "X3K_"})
            if depart_return_html:
                pass
            else:
                print("Not exist")
                print(soup)
            depart_html, return_html = depart_return_html
            self.scrape(new_flight.depart_flight, depart_html)
            self.scrape(new_flight.return_flight, return_html)
            
            self.flights.append(new_flight)

    def scrapeOneWay(self):
        """
        scrape all the nessesscary data and return the number of flights scraped
        date_leave->str, date_return->str: mm-dd-yyyy
        """
        url = self.returnUrl()
        self.driver.get(url)
        sleep(5)
        buttons = self.driver.find_elements(By.XPATH, "//div[@class='vJccne  trZjtf']")
        for button in buttons:
            button.click()
            sleep(0.5)

        flights = self.driver.find_elements(By.XPATH, "//li[@class='pIav2d']")

        for flight in flights:
            html_element = flight.get_attribute('outerHTML')
            soup = BeautifulSoup(html_element, "html.parser")

            new_flight = OneWayFlight()

            # print("_____________________________________________________________________________")
            temp_price = soup.find("div", {"class": "BVAVmf I11szd POX3ye"})
            price = temp_price.find("span", {"role": "text"}).text
            new_flight.price = price

            departures_texts = soup.find("div", {"class": "S90skc y52p7d ogfYpf"})
            # Departure_strings is a list of texts within the class but we only want the departure day
            departure_strings = [text for text in departures_texts.stripped_strings]
            new_flight.depart_day = departure_strings[1]

            # total_travel_time = soup.find("div", {"class":"gvkrdb AdWm1c tPgKwe ogfYpf"}).text
            # total_travel_times.append(total_travel_time)

            flight_duration_list = []
            depart_time = soup.find("div", {"class": "wtdjmc YMlIz ogfYpf tPgKwe"}).text
            arrive_time = soup.find("div", {"class": "XWcVob YMlIz ogfYpf tPgKwe"}).text
            flight_duration_list
            new_flight.flight_duration = f'{depart_time}-{arrive_time}'

            all_layovers = ""
            layover_info_list = soup.find_all("div", {"class": "tvtJdb eoY5cb y52p7d"})
            for layover in layover_info_list:
                layover = re.sub(r"\s+", '', layover.text)
                layover = layover.replace('layover', ' at ').replace('hr', 'h').replace('min', 'm')
                # Remove the redundant string after (airport code)
                layover_result, sep, _ = layover.partition(')')
                all_layovers += layover_result + sep + "\n"
            new_flight.layovers = all_layovers.rstrip("\n")

            all_airlines = soup.find_all("div", {"class": "MX5RWe sSHqwe y52p7d"})
            airlines_code_text = ""
            for airlines in all_airlines:
                airline = airlines.find("span", {"class": "Xsgmwe"}).text
                flight_code = airlines.find("span", {"class": "Xsgmwe sI2Nye"}).text
                flight_code = flight_code.replace(u'\xa0', u' ')
                airlines_code_text += airline + flight_code + '\n'

            new_flight.airlines_code = airlines_code_text.rstrip('\n')

            stop = soup.find("div", {"class": "EfT7Ae AdWm1c tPgKwe"}).get_text(strip=True)
            new_flight.stop = stop[0]

            self.flights.append(new_flight)

    def showOneWay(self):
        self.scrapeOneWay()
        for flight in self.flights:
            flight.printOneWayInfo()
    
    def showRoundTrip(self):
        self.scrapeRoundTrip()
        for flight in self.flights:
            flight.dataRoundTrip()


# if __name__ == "__main__":
#     s = Scraper("One Way", "SGN", "YVR", "01-25-2023", "03-01-2023")
#     s.showOneWay()