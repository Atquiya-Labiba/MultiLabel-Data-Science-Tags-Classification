from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import pandas as pd
import time

def main():    
    options = Options()
    options.headless = True    
    options.add_argument("--log-level=3")  
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) 

    base_url = "https://datascience.stackexchange.com/questions?tab=newest&pagesize=50"

    ques_urls = []
    for page_no in tqdm(range(1,491)):
        driver = webdriver.Chrome(options=Options)
        url=f"{base_url}&page={page_no}"
        driver.get(url)
        time.sleep(1)

        ques=driver.find_element(By.ID,"questions")
        rows=ques.find_elements(By.TAG_NAME,"h3")
        print(len(rows))
        for row in rows:
            url_tag=row.find_element(By.TAG_NAME,"a")
            ques_url=url_tag.get_attribute("href") 
            title=url_tag.text          

            ques_urls.append({
                "title": title,
                "url": ques_url
            })

        driver.quit()

        df = pd.DataFrame(data=ques_urls, columns=ques_urls[0].keys())
        df.to_csv("data/scraped/ques_urls.csv", index=False)

if __name__ == "__main__":
    main()