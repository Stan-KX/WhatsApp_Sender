import tkinter as tk
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from tkinter import messagebox
import os
import threading
from collections import OrderedDict
import psutil
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

#Version 022

def main():
    window()

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_experimental_option("detach", True)
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Failed to create driver: {e}")
        return None
    return driver
    
       
def send_message(msg, num, lbl_ind):
    driver = create_driver()
    driver.get("https://web.whatsapp.com")
    lbl_ind.config(text="Scan QR Code")
    QRpop = messagebox.askokcancel("Scan WhatsApp QR", "Press OK after Logging in.")       # Event to enable user to scan WhatsApp Web QR
    if QRpop:
        chats = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-icon='menu']")))
        if chats:
            numbers_list = list(num)
            message = msg
            failed_set = set()
            for i, number in enumerate(numbers_list, start=1):
                attempts = 0
                while attempts < 2:
                    try:
                        lbl_ind.config(text=f"Sending message {i} of {len(numbers_list)}: {number}")
                        driver.get(f"https://web.whatsapp.com/send?phone={number}&text={quote(message)}")
                        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Send"]')))
                        element.click()
                        time.sleep(3)
                        print(f"Message {i} of {len(numbers_list)} sent")
                        time.sleep(1)
                        break
                    except UnexpectedAlertPresentException as e:
                        lbl_ind.config(text=f"{e} occurred while trying to send message to {number}. Retrying...")
                        failed_set.add(number)
                        try:
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            print("Alert message:", alert_text)
                            alert.accept()
                        except NoAlertPresentException:
                            pass
                        time.sleep(2)
                        attempts += 1
                        continue
                    except NoAlertPresentException:
                        lbl_ind.config(text=f"No alert present while sending message to {number}. Retrying...")
                        failed_set.add(number)
                        time.sleep(2)
                        attempts += 1
                        continue

            if failed_set:
                lbl_ind.config(text=f"All messages sent. Message failed to send: {failed_set}")
                print(failed_set)
            else:
                lbl_ind.config(text="All messages sent.")


# Create the main window
def window():
    window = tk.Tk()
    current_scaling=window.tk.call('tk','scaling')
    new_scaling = 0.75
    window.tk.call('tk','scaling',new_scaling)
    window.title("WhatsApp Sender 0.2")
    window.resizable(width=False,height=True)

    # Create frames
    frame_title = tk.Frame(master=window, cursor="dot")
    frame_title.grid(columnspan=6, row=0, sticky="n", padx=5, pady=1)

    frame_ind = tk.Frame(master=window, cursor="dot")
    frame_ind.grid(columnspan=6, row=1, sticky="n", padx=5, pady=1)

    frame_ent = tk.Frame(master=window)
    frame_ent.grid(columnspan=3, row=2, sticky='nw', padx=5, pady=1)

    frame_ent2 = tk.Frame(master=window)
    frame_ent2.grid(columnspan=3, row=3, sticky='nw', padx=5, pady=1)

    frame_qr = tk.Frame(master=window)
    frame_qr.grid(column=4,row=2,columnspan=1,sticky='nsew',padx=1, pady=1)

    frame_btn=tk.Frame(master=window)
    frame_btn.grid(column=4,row=3,sticky='nsew',padx=2, pady=2)

    # Labels within frames
    lbl_title = tk.Label(master=frame_title, text="Welcome to WASender 0.2",
                        font=("Papyrus", 25), fg='white', bg='black')
    lbl_title.grid(column=0, row=0, sticky="nw", padx=15, pady=10)

    lbl_ind = tk.Label(master=frame_ind, text="Indicator", font=("Helvetica", 20))
    lbl_ind.grid(column=0, row=0, sticky='nsew')

    # Text widget within frame_ent

    msg_text = tk.Text(master=frame_ent, width=40, height=25, font="Arial, 15")  # Adjust width and height as needed
    msg_text.insert(tk.END, "Input your Message here.")  # Insert some text
    msg_text.tag_add("tag1", "1.0", "end")  # Apply the tag to the inserted text
    msg_text.tag_config("tag1", font=("papyrus", 20, "italic"))  # Configure the tag
    msg_text.grid(column=0, row=0, sticky='sw')  # Stick to top-left corner

    num_text = tk.Text(master=frame_ent2, width=40, height=25,font="Arial, 15")  # Adjust width and height as needed
    num_text.insert(tk.END, "Input your Recipients' numbers here, with each number on a new line.")  # Insert placeholder message
    num_text.tag_add("tag2", "1.0", "end")
    num_text.tag_config("tag2", font=("papyrus", 20, "italic"))  # Configure the tag
    num_text.grid(column=0, row=0, sticky='w')

    lbl_qr=tk.Label(master=frame_qr,text="Placeholder", font=("Helvetica", 10),bg="black",fg="white",relief="sunken",width=20,height=20)
    lbl_qr.grid(column=0, row=0, sticky='nwe')
    
    def btn1_click():
        num_dup = num_text.get("1.0",'end-1c').splitlines()
        num_set = set(OrderedDict.fromkeys(num_dup))
        num_text.delete("1.0",'end-1c')
        for num in num_set:
            num_text.insert(tk.END,num+"\n")
    
    # def btn2_click():                                 #Add Gemini api key and enable
    #     msg = msg_text.get("1.0",'end-1c')
    #     genai.configure(api_key="")
    #     model = genai.GenerativeModel('gemini-pro')
    #     prompt = f"Refine the grammar of this sentence:{msg}"
    #     response = model.generate_content(prompt)
    #     text = response.text
    #     msg_text.delete("1.0",'end-1c')
    #     msg_text.insert(tk.END,text)

    def btn3_click():
        confirmed = messagebox.askokcancel('Warning', 'To send messages, all Chrome windows will be closed.\n Do you wish to proceed?')
        if confirmed:
            for proc in psutil.process_iter():
                if "chrome" in proc.name().lower():
                    proc.kill()
                    time.sleep(1)
        else:
            return  
        num = num_text.get("1.0",'end-1c').splitlines()                           
        msg = msg_text.get("1.0",'end-1c')
        send_thread = threading.Thread(target=send_message,args=(msg, num,lbl_ind))
        send_thread.start()

    btn1_dup=tk.Button(master=frame_btn,text="Remove Duplicates", font=("Helvetica", 10),bg="black",fg="white",relief="sunken",width=20,height=5,command=btn1_click).grid(column=0, row=0, sticky='nwe')
    # btn2_ctr=tk.Button(master=frame_btn,text="Refine grammar", font=("Helvetica", 10),bg="black",fg="white",relief="sunken",width=20,height=5,command=btn2_click).grid(column=0, row=1, sticky='nwe')
    btn3_send=tk.Button(master=frame_btn,text="Send Now", font=("Helvetica", 10),bg="black",fg="white",relief="sunken",width=20,height=5,command=btn3_click,cursor="iron_cross").grid(column=0, row=3, sticky='nwe')
                    
    # Configure column and row weights
    for col in range(10):
        window.columnconfigure(col, weight=2)

    # Set row weights
    for row in range(10):
        window.rowconfigure(row, weight=2)


    # Start the main event loop
    window.mainloop()

if __name__=="__main__":
    main()