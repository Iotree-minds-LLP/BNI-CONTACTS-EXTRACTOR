from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import sys
import tkinter as tk
from tkinter import messagebox

def scrape_data(username, password):
    # Set up the webdriver
    driver = webdriver.Chrome()  # You can use any other webdriver as per your preference
    driver.get("https://www.bniconnectglobal.com/login/")

    # Find the username and password fields and submit button
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[1]/section[2]/div[2]/form[1]/div[1]/div/div/div/input')))
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[1]/section[2]/div[2]/form[1]/div[2]/div/div/div/input')))
    submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[1]/section[2]/div[2]/form[1]/div[3]/div/button')))

    # Enter the username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Click on the submit button
    submit_button.click()

    # Wait for the page to load after login
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

    # Find and click on the element specified by the new XPath after successful login
    element_to_click = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[2]/a[4]')))
    element_to_click.click() 

    # Initialize data list to store extracted information
    data = []

    while True:
        # Wait for the response table to load after clicking submit
        response_table_xpath = "/html/body/div[2]/div[1]/div[4]/div/div[2]/div[3]/table"
        response_table = WebDriverWait(driver, 6000).until(EC.presence_of_element_located((By.XPATH, response_table_xpath)))

        # Extract HTML content inside tbody, skipping the first two rows
        tbody_xpath = response_table_xpath + "/tbody"
        tbody_html = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, tbody_xpath))).get_attribute("innerHTML")
        tbody_html = "<tbody>" + tbody_html.split("<tbody>", 1)[-1]  # Excluding first two rows

        # Parse the HTML content
        soup = BeautifulSoup(tbody_html, "html.parser")

        # Extract desired information from each <tr> element
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 6:  # Only consider rows with 6 cells (excluding "More Results" and "Your search criteria produced no partial matches" rows)
                name = cells[0].text.strip()
                chapter = cells[1].text.strip()
                company = cells[2].text.strip()
                city = cells[3].text.strip()
                industry_and_classification = cells[4].text.strip()
                user_id = cells[0].find("a")["href"].split("=")[-1]  # Extract user ID from the href attribute
                data.append({
                    "Name": name,
                    "Chapter": chapter,
                    "Company": company,
                    "City": city,
                    "Industry and Classification": industry_and_classification,
                    "User ID": user_id
                })

        # Check if the "Next" button is enabled
        next_button = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[4]/div/div[2]/div[3]/div[2]/div[2]/span[4]')
        next_button_enabled = "ui-state-disabled" not in next_button.get_attribute("class")

        # If the "Next" button is enabled, click on it to go to the next page
        if next_button_enabled:
            time.sleep(1)
            next_button.click()
            time.sleep(1)
            next_button_enabled = "ui-state-disabled" not in next_button.get_attribute("class")
            # Wait for the next page to load
            #WebDriverWait(driver, 10).until(EC.staleness_of(response_table))
        else:
            break

    # Once all pages are processed, continue with extracting data from the last page
    # Extract HTML content inside tbody of the last page
    tbody_html = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, tbody_xpath))).get_attribute("innerHTML")
    tbody_html = "<tbody>" + tbody_html.split("<tbody>", 1)[-1]  # Excluding first two rows

    # Parse the HTML content of the last page
    soup = BeautifulSoup(tbody_html, "html.parser")

    # Extract desired information from each <tr> element of the last page
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) == 6:  # Only consider rows with 6 cells (excluding "More Results" and "Your search criteria produced no partial matches" rows)
            name = cells[0].text.strip()
            chapter = cells[1].text.strip()
            company = cells[2].text.strip()
            city = cells[3].text.strip()
            industry_and_classification = cells[4].text.strip()
            user_id = cells[0].find("a")["href"].split("=")[-1]  # Extract user ID from the href attribute
            data.append({
                "Name": name,
                "Chapter": chapter,
                "Company": company,
                "City": city,
                "Industry and Classification": industry_and_classification,
                "User ID": user_id
            })

    # Loop through the extracted data
    total_entries = len(data)
    for entry_num, entry in enumerate(data):
        user_id = entry["User ID"]
        # Open the user's profile page
        profile_url = f"https://www.bniconnectglobal.com/web/secure/networkHome?userId={user_id}"
        driver.get(profile_url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/div/label[5]/span[2]')))

        # Extract business information
        business_info_xpath = '/html/body/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/div/label[5]/span[2]'
        email_xpath = '/html/body/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/div/label[16]/span[2]/a'
        phone_xpath = '/html/body/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/div/label[8]/span[2]'
        mobile_xpath = '/html/body/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/div/label[11]/span[2]'

        business_info = driver.find_element(By.XPATH, business_info_xpath).text.strip()
        email = driver.find_element(By.XPATH, email_xpath).text.strip() if driver.find_elements(By.XPATH, email_xpath) else None
        phone = driver.find_element(By.XPATH, phone_xpath).text.strip() if driver.find_elements(By.XPATH, phone_xpath) else None
        mobile = driver.find_element(By.XPATH, mobile_xpath).text.strip() if driver.find_elements(By.XPATH, mobile_xpath) else None

        # Update the entry with additional information
        entry["Business Information"] = business_info
        entry["Email"] = email
        entry["Phone"] = phone
        entry["Mobile"] = mobile
        entry["Profile Link"] = "https://www.bniconnectglobal.com/web/secure/networkHome?userId="+str(user_id)


        # Update progress
        progress = (entry_num + 1) / total_entries
        print_progress(progress)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data)

    # Get the current date and time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Define the filename
    filename = f"bni_data_{current_timestamp}.xlsx"

    # Save the DataFrame to an Excel file
    df.to_excel(filename, index=False)

    print("File saved successfully with the name " + str(filename))

    # Close the webdriver
    driver.quit()

    return filename

def print_progress(progress):
    sys.stdout.write("\rProgress: [{:<50}] {:.2f}%".format('=' * int(progress * 50), progress * 100))
    sys.stdout.flush()

def on_submit():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password.")
        return

    submit_button.config(state=tk.DISABLED)
    status_label.config(text="Scraping data... Please wait.")

    # Run scraping function
    output_filename = scrape_data(username, password)

    status_label.config(text=f"Data saved to {output_filename}")
    submit_button.config(state=tk.NORMAL)

# Create Tkinter window
window = tk.Tk()
window.title("BNI Data Scraper")

# Username input
username_label = tk.Label(window, text="Username:")
username_label.grid(row=0, column=0, sticky="w")
username_entry = tk.Entry(window)
username_entry.grid(row=0, column=1)

# Password input
password_label = tk.Label(window, text="Password:")
password_label.grid(row=1, column=0, sticky="w")
password_entry = tk.Entry(window, show="*")
password_entry.grid(row=1, column=1)

# Submit button
submit_button = tk.Button(window, text="Submit", command=on_submit)
submit_button.grid(row=2, column=0, columnspan=2, pady=10)

# Status label
status_label = tk.Label(window, text="")
status_label.grid(row=3, column=0, columnspan=2)

window.mainloop()
