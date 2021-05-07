from Scraper import browser, googleads

if __name__ == '__main__':
    browser = browser.GABrowser()
    browser.get('https://ads.google.com/home/')
    googleads.navigate(browser)