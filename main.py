from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SkypeLogin:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=chrome_options)
        self.attempt_count = 0
        self.max_attempts = 5

    def handle_email_error(self):
        try:
            email_error = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "i0116Error"))
            )
            print(f"ERROR: {email_error.text}")
            email_input = self.driver.find_element(By.ID, "i0116")
            email_input.send_keys(Keys.CONTROL + "a")
            email_input.send_keys(Keys.DELETE)
            return True
        except Exception:
            return False

    def handle_login_error(self, error_id):
        try:
            error_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, error_id))
            )
            error_message = error_element.text
            print(f"ERROR: {error_message}")
            self.attempt_count += 1
            return True
        except Exception:
            return False

    def decline_stay_signed_in(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "kmsiTitle"))
            )
            decline_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "declineButton"))
            )
            decline_button.click()
            print("Declined 'Stay signed in?' prompt")
        except Exception as e:
            print("Stay signed in prompt not shown or failed to interact:", e)

    def login(self):
        try:
            self.driver.get("http://web.skype.com/")

            # Email input loop
            while True:
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "i0116"))
                )
                email = input("Enter email: ")
                email_input.send_keys(email)
                email_input.send_keys(Keys.RETURN)

                if not self.handle_email_error():
                    break

            # Determine login method
            next_prompt = WebDriverWait(self.driver, 60).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "i0118")),
                    EC.presence_of_element_located((By.ID, "idTxtBx_OTC_Password")),
                )
            )

            while self.attempt_count < self.max_attempts:
                if next_prompt.get_attribute("id") == "i0118":
                    print("Password login detected")
                    password = input("Enter password: ")
                    next_prompt.send_keys(password)
                    next_prompt.send_keys(Keys.RETURN)

                elif next_prompt.get_attribute("id") == "idTxtBx_OTC_Password":
                    print("OTC login detected")
                    otc = input("Enter OTC: ")
                    next_prompt.send_keys(otc)
                    next_prompt.send_keys(Keys.RETURN)

                if self.handle_login_error("idTD_Error"):
                    self.driver.quit()
                    return
                if self.handle_login_error("i0118Error"):
                    continue
                if self.handle_login_error("idTxtBx_OTC_Password_Error"):
                    continue

                # Successfully logged in
                break

            if self.attempt_count >= self.max_attempts:
                print("Max attempts reached. Exiting...")
                self.driver.quit()
                return

            self.decline_stay_signed_in()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-1dbjc4n"))
            )
            print("Login successful")

        except Exception as e:
            print(f"An error occurred during login: {str(e)}")
        finally:
            self.driver.quit()


if __name__ == "__main__":
    skype_login = SkypeLogin()
    skype_login.login()