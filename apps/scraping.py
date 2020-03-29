# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def scrape_all():
   # Initiate headless driver for deployment
   browser = Browser("chrome", executable_path="chromedriver", headless=True)
   news_title, news_paragraph = mars_news(browser)
   # Run all scraping functions and store results in dictionary
   data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_images(browser),
      "hemisphere_info": hemispheres(browser),
      "facts": mars_facts(browser),
      "last_modified": dt.datetime.now()
        }
   return data

def mars_news(browser):

   # Visit the mars nasa news site
   url = 'https://mars.nasa.gov/news/'
   browser.visit(url)
   # Optional delay for loading the page
   browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

   # Convert the browser html to a soup object and then quit the browser
   html = browser.html
   news_soup = BeautifulSoup(html, 'html.parser')

   try:

    slide_elem = news_soup.select_one('ul.item_list li.slide')
    # Use the parent element to find the first <a> tag and save it as `news_title`
    news_title = slide_elem.find("div", class_='content_title').get_text()
    # Use the parent element to find the paragraph text
    news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

   except AttributeError:
    return None, None

   return news_title, news_p   

### Featured Images

def featured_images(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def hemispheres(browser):
    # Visit the mars nasa news site
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # scrapes for all headers of each hemisphere
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    search_titles = news_soup.find_all('h3')

    titles = []
    for x in search_titles:
        title = []
        title.append(str(x))
        for x in title:
            titles.append(x[4:-5])


    # scrapes and stores each hemispheres full size image link in list
    img_url = []

    for header in titles:
        info = browser.find_link_by_partial_text(header)
        info.click()
    
        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')

        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='wide-image').get("src")

        img_url.append(f'https://astrogeology.usgs.gov{img_url_rel}')
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)

    # creates a list of dictionaries for each hemisphere of Mars
    hemispheres = []

    # adds header as title to individual dictionaries
    for title in titles:
        sphere = {
                'title': title,
            }
        hemispheres.append(sphere)
    
    # adds a key value pair to each dictionary in hemispheres for image link
    for item in hemispheres:
        item.update({"img_url": "value"} )
    
    
    # adds the full size image link to indivual dictionary
    counter = 0
    for d in hemispheres:
        d.update(img_url = img_url[counter])
        counter += 1
    return hemispheres

def mars_facts(browser):

    try:

 
        # Sets up dataframe from HTML of desired webpage
        mdf = pd.read_html('http://space-facts.com/mars/')[0]
        edf = pd.read_html('http://space-facts.com/earth/')[0]

    except BaseException:
        return None
    mdf.columns=['Description', 'Mars']
    edf.columns=['Description', 'Earth']
    df = pd.merge(mdf,edf, on='Description')    
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    return df.to_html()


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())