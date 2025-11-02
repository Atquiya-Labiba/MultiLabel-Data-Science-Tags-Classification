from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import pandas as pd
import time
from multiprocessing import Pool, cpu_count

def scrape_question_details(url,driver,wait):
    try:
        driver.get(url)           

        try:
            # Question Title Scraping
            title_cont= wait.until(EC.presence_of_element_located((By.ID, "question-header")))
            tag=title_cont.find_element(By.TAG_NAME, "a")
            title = tag.text.strip()

            print("Question Title: ", title)
        except:
            title = None

        try:
            # Question Description Scraping
            description = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".s-prose.js-post-body"))).text
        except:
            description = None 

        try:
            # Question Tags Scraping
            tag_cont=wait.until(EC.presence_of_element_located((By.CLASS_NAME,"post-taglist")))
            list_items=tag_cont.find_elements(By.TAG_NAME,"li")
            tags = [li.text.strip() for li in list_items if li.text.strip()]

            print("Question Tags", tags)
        except:
            tags = None
                  
        return{
            "title": title,
            "description": description,
            "tags": tags,
            "url": url
        }
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {
            'title': None,
            'description': None,
            'tags': None,
            'url': url            
        }


def scrape_chunk(args):
    url_chunks,chunk_id=args
    options = Options()     
    options.add_argument("--headless=new") 
    options.add_argument("--log-level=3")  
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) 
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-background-networking")  
    options.add_argument("--disable-sync")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 5)

    ques_details=[]

    try:
        for url in tqdm(url_chunks, desc=f"Process {chunk_id}", position=chunk_id, leave=False):
            data = scrape_question_details(url,driver,wait)
            ques_details.append(data)  

            time.sleep(0.1)             
         
        print(f"Process {chunk_id} completed")
        return ques_details
    except Exception as e:
        print(f"Process {chunk_id} error: {str(e)}")
        return ques_details
    finally:
        driver.quit()


def main():
    
    df=pd.read_csv("data/scraped/ques_urls.csv")
    ques_urls=df["url"].to_list()

    num_processes=min(cpu_count(), 6)
    print(f"Using {num_processes} processes (CPU cores: {cpu_count()})")

    total_urls=len(ques_urls)
    print(total_urls) #24500 urls   

    
    # Divide URLs among processes
    partition_size = (len(ques_urls) // num_processes) + 1
    url_chunks = [(ques_urls[i:i + partition_size], idx) 
        for idx, i in enumerate(range(0, total_urls, partition_size))]
    
    all_results=[]       
    with Pool(processes=num_processes) as pool:
        for chunk_results in pool.imap_unordered(scrape_chunk, url_chunks):
            all_results.extend(chunk_results)

            # Save after each chunk
            pd.DataFrame(all_results).to_csv("data/scraped/ques_details.csv", index=False)            

    # Final save at the end
    pd.DataFrame(all_results).to_csv("data/scraped/ques_details.csv", index=False)
    print(f"Total records: {len(all_results)}")          
          

if __name__ == "__main__":
    main()