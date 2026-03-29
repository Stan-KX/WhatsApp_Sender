import tkinter as tk
import time
import threading
import psutil
from urllib.parse import quote
from tkinter import messagebox
from collections import OrderedDict
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_message(msg, num_list, lbl_ind):
    # Driver initialization - 'uc=True' handles the 'Undetected' part
    # 'incognito=True' helps prevent cache bloat, but remove it if you want to stay logged in
    driver = Driver(uc=True, headless=False) 
    
    try:
        driver.get("https://web.whatsapp.com")
        lbl_ind.config(text="Scanning QR Code...")

        # Wait for the main interface to load after QR code scan
        # CSS Selector targeting the chat list button, which only appears after successful login
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-controls='chat-list']"))
        )

        for i, number in enumerate(num_list, start=1):
            # Clean number: Keep only digits
            clean_number = "".join(filter(str.isdigit, number))
            if not clean_number:
                continue
            
            lbl_ind.config(text=f"Progress: {i}/{len(num_list)} | Messaging: {clean_number}")
            
            direct_url = f"https://web.whatsapp.com/send?phone={clean_number}&text={quote(msg)}"
            driver.get(direct_url)

            try:
                # 1. Look for 'data-testid' (WhatsApp's internal testing hooks)
                # 2. Look for 'aria-label' (Accessibility tags required for screen readers)
                send_selector = "button[data-testid='compose-btn-send'], button[aria-label='Send']"
                
                send_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, send_selector))
                )
                
                # Small human-like delay before clicking
                time.sleep(1.5)
                send_btn.click()
                
                # Wait for the 'Sent' checkmark or for the text box to clear
                time.sleep(3) 
                print(f"Success: {clean_number}")

            except Exception as e:
                # This catches 'Invalid Number' overlays or loading timeouts
                print(f"Error sending to {clean_number}: Number might be invalid or UI changed.")
                # Optional: Capture a screenshot for debugging if it fails
                # driver.save_screenshot(f"error_{clean_number}.png")

        lbl_ind.config(text="Bulk operation complete.")
        messagebox.showinfo("Done", "All messages processed.")

    except Exception as total_failure:
        lbl_ind.config(text="An error occurred.")
        print(f"Critical Failure: {total_failure}")
    
    finally:
        time.sleep(5)
        driver.quit()

def window():
    root = tk.Tk()
    root.title("WhatsApp Sender 2026 Edition")
    
    # Simple UI Styling
    root.configure(bg="#2c3e50")
    
    main_frame = tk.Frame(root, bg="#2c3e50")
    main_frame.pack(padx=20, pady=20)

    lbl_title = tk.Label(main_frame, text="WA Bulk Sender", font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#2c3e50")
    lbl_title.pack(pady=10)

    lbl_ind = tk.Label(main_frame, text="Ready to start", font=("Arial", 12), fg="#f1c40f", bg="#2c3e50")
    lbl_ind.pack(pady=5)

    # Input Areas
    tk.Label(main_frame, text="Message Content:", fg="white", bg="#2c3e50").pack(anchor="w")
    msg_text = tk.Text(main_frame, width=50, height=10, font=("Arial", 11))
    msg_text.pack(pady=5)

    tk.Label(main_frame, text="Phone Numbers (One per line):", fg="white", bg="#2c3e50").pack(anchor="w")
    num_text = tk.Text(main_frame, width=50, height=10, font=("Arial", 11))
    num_text.pack(pady=5)

    # Logic for buttons
    def clean_duplicates():
        numbers = num_text.get("1.0", tk.END).splitlines()
        unique_numbers = list(OrderedDict.fromkeys([n.strip() for n in numbers if n.strip()]))
        num_text.delete("1.0", tk.END)
        num_text.insert(tk.END, "\n".join(unique_numbers))

    def on_send_click():
        # Kill Chrome to prevent profile lock issues
        if messagebox.askokcancel("Confirm", "Close all Chrome instances and start?"):
            for proc in psutil.process_iter(['name']):
                if "chrome" in proc.info['name'].lower():
                    try: proc.kill()
                    except: pass
            
            msg = msg_text.get("1.0", "end-1c")
            nums = num_text.get("1.0", "end-1c").splitlines()
            
            # Run in a thread so the UI doesn't freeze
            thread = threading.Thread(target=send_message, args=(msg, nums, lbl_ind), daemon=True)
            thread.start()

    # Buttons
    btn_frame = tk.Frame(main_frame, bg="#2c3e50")
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="Remove Duplicates", command=clean_duplicates, width=20).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="START SENDING", command=on_send_click, bg="#27ae60", fg="white", width=20, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)

    root.mainloop()

if __name__ == "__main__":
    window()