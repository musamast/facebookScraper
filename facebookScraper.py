# # Importing all Required libraries
import os
import re
import time
import getpass
import csv 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


##  setting up chrome driver options
chrome_option = Options()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_option.add_experimental_option("prefs",prefs)
# chrome_option.add_argument("--headless") ## comment this if you want to see browser scraping pages
driver=webdriver.Chrome(executable_path=os.path.abspath('chromedriver.exe'),options=chrome_option) ## path of chrome driver


## for logging into facebook
def login(user,password):
    try:
        print('Logging into Facebook ..')
        driver.get('https://www.facebook.com/') ## facebook login url
        driver.find_element_by_name('email').send_keys(user) ## user = facebook phone/email
        driver.find_element_by_name('pass').send_keys(password) ## password = facebook password
        driver.find_elements_by_css_selector("input[type=submit]")[0].click() ## log in button
        print('Successfully logged into Facebook ..')
    except NoSuchElementException as exception:
        print ("Element not found on login page : ")
    except Exception as exception:
        print ("Cannot log in to facebook : ")

## search pages for given keyword and number of pages want
def search(keyword,page_count):
    driver.get(f'https://www.facebook.com/search/pages/?q={keyword}') ## search query
    oldlen=len(driver.find_elements_by_class_name('_32mo')) ## number of pages on first display
    while oldlen < int(page_count): ## looping while pages displaying on first hit is less than required pages
        oldlen=len(driver.find_elements_by_class_name('_32mo'))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") ## scrolling window down if number pages display is less than required pages
        time.sleep(3)
        newlen=len(driver.find_elements_by_class_name('_32mo')) ## increment in number of pages displaying
        if newlen == oldlen: ## stoping loop if no more pages available 
            break

def fetch_data():
    with open(f'{keyword}.csv', 'a') as csvfile:  ## creating csv files named based on keyword
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["page_name" ,"likes" ,"email", "category" ,"location" ,"phone" ,"fb_page" ,"website"]) ## writing header
    count=0
    try:
        print(f"Scraping Result and saving into {keyword}.csv ")
        for link in driver.find_elements_by_class_name('_32mo'): ## looping on number of pages
            if count == int(page_count): ## stopping loop if required number of pages are scraped
                 break
            page_name =''
            likes = ''
            email =  ''
            category = ''
            location = ''
            phone = ''
            fb_page =  ''
            website =  ''   
            time.sleep(2)
            href=link.get_attribute('href')
            driver.execute_script("window.open('%s', 'new_window')"%href) ## get url of page and open in new tab
            driver.switch_to.window(driver.window_handles[1]) ## changing main window of driver to new page tab
            time.sleep(5)
            try:
                page_name=driver.find_element_by_id('seo_h1_tag').text ## getting page name
            except Exception as e:
                print(f"Title not found for {page_name}")
            try:
                for i in driver.find_elements_by_class_name('_4bl9'): ## getting page likes
                    if 'people like this' in i.text:
                        likes=i.text.split()[0] ## ignoring 'people like this' from likes
                        break
            except Exception as exception:
                print(f"Likes not found for {page_name}")
            fb_page=driver.current_url ## page url
            time.sleep(5)
            try:
                for about in driver.find_elements_by_class_name('_2yau'):
                    if about.text == 'About':
                        about.click() ## clicking on 'about' page of fb page
                        break
            except Exception as exception:
                print(f"Cant click on about page for {page_name}")    
            time.sleep(7)
            try:
                category=driver.find_element_by_css_selector('._4bl9._5m_o').text ## page category
            except Exception as e:
                print(f"Category not found for {page_name}")
            try:
                location=driver.find_element_by_css_selector('._5aj7._3-8j._20ud').text.replace('\n',' ').replace('Get Directions','') ## page location ignoring other non wanted info
            except NoSuchElementException as exception:
                print(f"Location not found for {page_name}") ## will display 'location not found if page location not available
            except Exception as e:
                print(f"Location not found for {page_name}")
            try:
                for i in driver.find_elements_by_class_name('_4bl9'): ## looping all elements of class '_4b19'
                    if 'Call' in i.text: ## if call in string its phone number
                        phone = re.sub(r"[a-z]", "", i.text.replace('\n',' '), flags=re.I)  ## regular ex for matching string is valid phone
                    elif re.match("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",i.text): ## regular ex for matching string is valid website url
                        website=i.text
                    else:
                        for word in i.text.split():
                            if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", word): ## regular ex for matching string is valid email
                                email=word    
            except Exception as e:
                print(f"Cant Fetch data of class '_4b19' for {page_name}")            
            with open(f'{keyword}.csv', 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([page_name ,likes ,email, category ,location ,phone ,fb_page ,website]) ## writing all fetched data into csv file
            count+=1 ## incrementing 1 in number of pages scraped
            print(f'Total Pages Scraped : {count}' )     
            driver.close() ## close page tab
            driver.switch_to.window(driver.window_handles[0]) ## changing main window of driver back to search page    
    except NoSuchElementException as e:
        print('Element not found on search page : ')
    print(f"{count} pages successfully scraped and saved into {keyword}.csv")
    driver.close()       
    



if __name__ == '__main__': ## calling all functions in main function
    user=input('Enter Facebook username/email: ')
    password=getpass.getpass('Enter Facebook password:')
    login(user,password)
    # login('user','pass')  ## uncomment this and comment user,password variables and login func and gived hardcoded pass and user if dont want to give logging details every time
    keyword=input('Enter keyword you want to search: ')
    page_count=input('Enter max number of pages you want to search: ')
    search(keyword,page_count)
    time.sleep(5)
    fetch_data()
