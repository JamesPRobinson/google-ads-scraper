from datetime import datetime as dt
import glob
import numpy as np
from os import path
import pandas as pd
import pyautogui
import pyperclip
import re
from selenium.webdriver.common.keys import Keys
from settings import get_encoding, INPUT_FOLDER, MISSING_KWD_FILE, OUTPUT_FOLDER
import time
import traceback

# In setting the Google Ads date for records to pull from
SetDate = False

# - Keywords do not contains illegal characters: ! @ % ^ () = {} ; ~ ` <> ? \ | *
# Therefore we trim these (keywords) out...
chars_to_remove = ['!', '@', '%', '^', '(',')', '=', '{', '}', ';', '~', '`', '<', '>', '?', '\\', '|', '*']
rx = '[' + re.escape(''.join(chars_to_remove)) + ']'

# Google Ads stipulates:
# - Keywords per line no longer than 80 characters
# - Keywords per line no longer than 10 words in a sentence
def CheckSplit(s):
    if isinstance(s, str):
        return len(s.split()) < 10 and len(s) < 80
    return False


def write_missing(terms):
    missing_df = pd.DataFrame({"Keywords" : terms})
    missing_df.to_csv(MISSING_KWD_FILE, header=False, index=False, mode='a')


def run_query(ga):
    # Select Discover New Keywords
    ga.clickElement("//span[text()='Get search volume and forecasts']")
    ga.clickElement("//textarea[contains(@aria-label,'Enter or paste your keywords,')]", 100)
    txtbox = ga.getElement("//textarea[contains(@aria-label,'Enter or paste your keywords,')]", 100)
    txtbox.send_keys(Keys.CONTROL,'v')
    # Confirm keywords
    ga.clickElement("//material-button[contains(@class,'get-results-button')]", 100)
    time.sleep(10)
    ga.clickElement('//a[contains(@href, "forecast")]')
    # Select calendar and confirm longest time span, only needs to be set once (or twice?) per session
    global SetDate
    if not SetDate:
        input("Press Enter when you have set date: ")
        SetDate = True
    ga.clickElement("//dropdown-button[contains(@class, 'bid-strategy')]", 100)
    ga.clickElement('//material-dropdown-select[contains(@popupclass, "strategy")]', 100)
    ga.clickElement("//span[text()='Manual CPC']", 100)
    ga.clickElement('//material-button[contains(@class, "apply")]', 100)

    # Select CPC input and change value
    ga.clickElement("//span[contains(@class, 'summary-value')]", 100)
    ga.clickElement("//span[contains(@class, 'summary-field maxCpc')]", 100)
    ga.clickElement("//span[contains(@class, 'summary-field maxCpc')]", 100)
    ga.clickElement("//input[@type='money64']")
    max_cpc_text = ga.getElement("//input[@type='money64']", 100)
    max_cpc_text.send_keys(Keys.CONTROL, 'a')
    max_cpc_text.send_keys(Keys.BACKSPACE)
    max_cpc_text.send_keys('200')
    ga.clickElement("//input[@type='money64']", 100)
    cpc_val = None
    # aiming to grab max value from google error text, default to safe value of 1 and retrieve records if fails
    try:
        cpc_warning = ga.getElement("//div[contains(@class, 'error-text')]", 100)
        for word in cpc_warning.text.split():
            try:
                cpc_val = float(word)
            except ValueError:
                continue
        if not cpc_val:
            cpc_val = 1
    except:
        cpc_val = 1
    ga.clickElement("//span[contains(@class, ' maxCpc')]", 100)
    max_cpc_text = ga.getElement("//input[@type='money64']", 100)
    max_cpc_text.send_keys(Keys.CONTROL, 'a')
    max_cpc_text.send_keys(Keys.BACKSPACE)
    max_cpc_text.send_keys(str(cpc_val))
    pyautogui.hotkey('enter')
    time.sleep(3)
    # csv icon
    ga.clickElement("//material-menu[contains(@class,'download')]//material-button[contains(@class,'trigger')]", 15)
    # csv_icon_forecast 
    time.sleep(2)
    ga.clickElement("//material-select-item[contains(@aria-label, 'csv') and contains(@data-group-index, '0')]", 15)
    time.sleep(5)
    ga.clickElement("//material-menu[contains(@class,'download')]//material-button[contains(@class,'trigger')]", 15)
    time.sleep(2)
    # csv_icon_stats
    ga.clickElement("//material-select-item[contains(@aria-label, 'csv') and contains(@data-group-index, '1')]", 15)
    # wait for files to download properly before searching for them in folder
    time.sleep(10)
    ga.clickElement("//material-button[contains(@class,'back')]", 100)


def navigate(ga):
    setup_files = glob.glob(str(INPUT_FOLDER) + "/*.csv")
    bcs, lcs = None, None
    try:
        bcs = [e.lower() for e in setup_files if 'bc' in e or 'business' in e][0]
    except IndexError as exc:
        print("No file in folder 'Input' relating to business categories in format '.csv'.")
        return
    try:
        lcs = [e.lower() for e in setup_files if 'lc' in e or 'local' in e][0]
    except IndexError as exc:
        print("No file in folder 'Input' relating to localities in format '.csv'.")
        return
    bcs = pd.read_csv(bcs, encoding=get_encoding(bcs))
    lcs = pd.read_csv(lcs, encoding=get_encoding(lcs))
    combined = lcs.assign(key=1).merge(bcs.assign(key=1), on='key').drop('key',axis=1)
    # Offset cycling through GAds to user = greater flexibility?
    # ga.clickElement('//a[contains(@href, "login")]')
    input("Hit enter in the terminal when signed in & the Keyword Planner page loaded.")   
    for bc in bcs["name"]:
        # Get all terms applicable to bc
        # name_x = bc name, name_y = locality name
        records = combined[combined['name_y'].str.endswith(bc)]
        search_terms = []
        for i in range(1, 4):
            search_terms.append(records["name_x"] + " " + records[f'elite_keyword{i}'])
        search_terms = [re.sub(rx, '', x) for y in search_terms for x in y if CheckSplit(x)]
        terms = ', '.join(search_terms)
        # copy elongated string to clipboard
        pyperclip.copy(terms)
        try:
            run_query(ga)
            # Get all csv files downloaded from ga & find latest additions
            path = r'Raw_Output'         
            all_files = glob.glob(path + "/*.csv")
            forecast = max([e for e in all_files if 'Fore' in e], default=None, key=path.getctime)
            stats = forecast = max([e for e in all_files if 'Stat' in e], default=None, key=path.getctime)
            if forecast and stats:
                res = write_bc(bc, forecast, stats)
                if not res:
                    raise FileNotFoundError(f"File not found for BC: {bc}")                  
        except Exception as e:
            traceback.print_exc()
            print(e)
            write_missing(search_terms)
            ga.clickElement("//material-button[contains(@class,'back')]")


def write_bc(bc, forecast, stats):
    try:
        fc = pd.read_csv(forecast, header = 0, dtype=str, sep = '\t', encoding='utf_16', engine='python',
                            usecols=['Keyword', 'Estimated CTR', 'Estimated Average CPC']) 
        st = pd.read_csv(stats, header = 2, dtype=str, sep = '\t', encoding='utf_16', engine='python',
                            usecols=['Keyword', 'Avg. monthly searches', 'Competition (indexed value)'])
        fc["Keyword"] = fc["Keyword"].lower()
        st["Keyword"] = st["Keyword"].lower()
        if bc.lower() in fc["Keyword"] and bc.lower() in st["Keyword"]:
            fc.dropna(inplace=True, subset=['Keyword'])
            fc['Estimated CTR'] = fc['Estimated CTR'].replace(np.nan, 0.0)
            fc['Estimated Average CPC'] = fc['Estimated Average CPC'].replace(np.nan, 0.0)

            st.dropna(inplace=True, subset=["Keyword"])
            st['Avg. monthly searches'] = st['Avg. monthly searches'].replace(np.nan, 0.0)
            st['Competition (indexed value)'] = st['Competition (indexed value)'].replace(np.nan, 0.0)

            stats_forecast = st.merge(fc, on="Keyword")
            stats_forecast.drop_duplicates(inplace=True, subset=['Keyword'])
            res_filename = f"BC_Output/{bc}-KeywordPlannerData.csv" 
            stats_forecast.to_csv(res_filename, index=False, mode='w')
            return os.path.exists(res_filename)
    except Exception as e:
        print(e)
    return False