from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from requests.models import PreparedRequest

import csv
import os


class AutobazarEuScraper():
    def __init__(self) -> None:
        
        RELATIVE_DRIVER_PATH = 'chromedriver_win32\chromedriver.exe'
        DRIVER_PATH = os.getcwd() + '\\' + RELATIVE_DRIVER_PATH

        options = Options()
        options.add_argument('--log-level=3') #Silence annoying log messages from console
        
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)        
        self.BASE_URL = "https://www.autobazar.eu/"

        self.brand_to_value = {}
        self.brandmodel_to_value = {}
        
    def get_brands_and_models(self):

        self.brand_to_value = {}
        self.brandmodel_to_value = {}

        # Not needed to save, therefore lack of self. 
        # Will be returned to the caller
        brand_to_models = {} 

        self.driver.get(self.BASE_URL)
        brand_list = Select(self.driver.find_element(By.ID, "BrandID"))

        # Skip the placeholder option by [1:]
        # Iterate over all car brand options
        for brand_option in brand_list.options[1:]:
                brand = brand_option.text
                self.brand_to_value[brand] = brand_option.get_attribute("value")

                # Now that I have saved brand to value
                # I will check all the models this brand has
                brand_to_models[brand] = []
                self.brandmodel_to_value[brand] = {}
                
                brand_list.select_by_value(self.brand_to_value[brand])
                models_list = Select(self.driver.find_element(By.ID, "CarModelID"))
                
                # Skip the placeholder option by [1:]
                # And now iterate over all models current brand has
                for model_option in models_list.options[1:]:
                    model_name = model_option.text
                    brand_to_models[brand].append(model_name)
                    self.brandmodel_to_value[brand][model_name] = model_option.get_attribute("value")

        return list(self.brand_to_value.keys()), brand_to_models
    
    # get_brands_and_models has to be called before this function
    def scrape_brand_model(self, brand: str, model: str, save_name: str):
        print(f"Starting to scrape {brand} {model} offerings.")

        scrape_result = []
        #START Select combination
        self.driver.get(self.BASE_URL)
        #Get brand_list and models_list
        brands_list = Select(self.driver.find_element(By.ID, "BrandID"))
        models_list = Select(self.driver.find_element(By.ID, "CarModelID"))

        brands_list.select_by_value(self.brand_to_value[brand])
        models_list.select_by_value(self.brandmodel_to_value[brand][model])

        submit_button = self.driver.find_element(By.ID, "searchgo")
        submit_button.submit()
            
        page_i = 1
        current_url = self._update_url_with_params(self.driver.current_url, {"page": page_i})
        print(f"current_url == {current_url}")
        print("__________________")

        #START Scrape
        while(True):

            listed_items_descriptions_elements = self.driver.find_elements(By.CLASS_NAME, "listitem-description")
            if(len(listed_items_descriptions_elements) == 0):
                #print(f"Done {brand} {model} with page_i == {page_i}")
                break
            #print(f"Loading {brand} {model} for page_i == {page_i}")

            for listed_item_description in listed_items_descriptions_elements:

                # Extract data
                scrape_result.append({
                    "price" : self._get_listed_item_description_price(listed_item_description),
                    "year"  : self._get_listed_item_description_year(listed_item_description),
                    "trans" : self._get_listed_item_description_trans(listed_item_description),
                    "fuel"  : self._get_listed_item_description_fuel(listed_item_description),
                    "km"    : self._get_listed_item_description_km(listed_item_description),
                    "kw"    : self._get_listed_item_description_kw(listed_item_description)
                })
                print("__________________")


            page_i += 1            
            # EXPLANATION
            # current_url[:-(len("page=") + len(str(page_i)) + 1)] is current url without page variable
            # {"page": page_i} adds the page variable back but with updated value
            # update_url_with_params makes from these 2 arguments new url for next page
            # More elegant solution would be nice
            current_url = self._update_url_with_params(current_url[:-(len("page=") + len(str(page_i)) + 1)], {"page": page_i})
            self.driver.get(current_url)
            
        # Scraping Ended
        # Now save the result as .csv   
        with open(save_name + ".csv", 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = ["price", "year", "trans", "fuel", "km", "kw"])
            writer.writeheader()
            writer.writerows(scrape_result)
        # Scrape function end

    def _update_url_with_params(self, url, params):
        req = PreparedRequest()
        req.prepare_url(url, params)
        return req.url

    def _get_listed_item_description_price(self, listed_item_description, timeout=5):   

        # Returns price in Euros if possible (Czech crowns are being automaticaly converted, otherwise return is None)
        def get_int_price_from_string(price_str):
            #If there is no number return None - case with "cena dohodou"
            if((price_str.isalpha()) or (price_str == "") or ("," in price_str)):
                return None

            EUR_TO_CZK = 25
            split_price_str = price_str.split()
            currency = split_price_str[-1]

            if(currency != "Kč" and currency != "€"):
                return None
            
            ret = ""
            for part_str in split_price_str[:-1]:
                ret += part_str
            ret = int(ret)

            if(currency == "Kč"):
                ret /= EUR_TO_CZK

            return int(ret)

        try:
            price_str = WebDriverWait(listed_item_description, timeout).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class=\"listitem-price\"]//a")))
            price_str = price_str.text
        except:
            print("EXCEPTION CAUGHT - Element's price not found")
            price_str = ""

        price_int = get_int_price_from_string(price_str)
        #PASSED
        #print(f"price_str = {price_str}")
        print(f"price_int = {price_int}")

    def _get_listed_item_description_year(self, listed_item_description, timeout=5):   

        try:
            year_str = WebDriverWait(listed_item_description, timeout).until(EC.visibility_of_element_located((By.XPATH, ".//span[@class=\"listitem-info-year\"]")))
            year_int = int(year_str.text)
        except:
            print("EXCEPTION CAUGHT - Element's year not found")
            year_int = None

        print(f"year_int = {year_int}")
        return year_int
        
    def _get_listed_item_description_trans(self, listed_item_description, timeout=5):
    
        try:
            trans = (WebDriverWait(listed_item_description, timeout).until(EC.visibility_of_element_located((By.XPATH, ".//span[@class=\"listitem-info-trans\"]")))).text
        except:
            print("EXCEPTION CAUGHT - Element's trans not found")
            trans = None

        print(f"trans = {trans}")
        return trans

    def _get_listed_item_description_km(self, listed_item_description, timeout=5):
    
        try:
            km_str_tmp = (WebDriverWait(listed_item_description, timeout).until(EC.visibility_of_element_located((By.XPATH, ".//span[@class=\"listitem-info-km\"]")))).text
            km_str = ""

            for nums in km_str_tmp.split()[:-1]:
                km_str += nums

            km_int = int(km_str)
        except:
            print("EXCEPTION CAUGHT - Element's km_int not found")
            km_int = None

        print(f"km_int = {km_int}")
        return km_int
        
    def _get_listed_item_description_kw(self, listed_item_description, timeout=5):
    
        try:
            kw_str = (WebDriverWait(listed_item_description, timeout).until(EC.visibility_of_element_located((By.XPATH, ".//span[@class=\"listitem-info-kw\"]")))).text
            kw_int = int(kw_str.split()[0])
        except:
            print("EXCEPTION CAUGHT - Element's kw not found")
            kw_int = None

        print(f"kw_int = {kw_int}")
        return kw_int

    def _get_listed_item_description_fuel(self, listed_item_description, timeout=5):
            try:
                fuel = (WebDriverWait(listed_item_description, timeout).until(EC.visibility_of_element_located((By.XPATH, ".//span[@class=\"listitem-info-fuel\"]")))).text
            except:
                print("EXCEPTION CAUGHT - Element's fuel not found")
                fuel = None

            print(f"fuel = {fuel}")
            return fuel