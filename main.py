from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


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

    def wait_for_element(self, by, value, condition=EC.presence_of_element_located, timeout=10):
        return WebDriverWait(self.driver, timeout).until(condition((by, value)))

    def handle_email_error(self):
        try:
            email_error = self.wait_for_element(By.ID, "i0116Error", timeout=5)
            print(f"ERROR: {str(email_error.text)}")
            email_input = self.wait_for_element(By.ID, "i0116")
            email_input.send_keys(Keys.CONTROL + "a")
            email_input.send_keys(Keys.DELETE)
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def handle_login_error(self, error_id):
        try:
            error_element = self.wait_for_element(By.ID, error_id, timeout=5)
            print(f"ERROR: {str(error_element.text)}")
            self.attempt_count += 1
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def decline_stay_signed_in(self):
        try:
            self.wait_for_element(By.ID, "kmsiTitle", timeout=10)
            decline_button = self.wait_for_element(By.ID, "declineButton", condition=EC.element_to_be_clickable)
            decline_button.click()
            print("Declined 'Stay signed in?' prompt")
        except (NoSuchElementException, StaleElementReferenceException):
            pass

    def login(self):
        try:
            self.driver.get("http://web.skype.com/")

            # Email input loop
            while True:
                email_input = self.wait_for_element(By.ID, "i0116", timeout=10)
                email = input("Enter email: ")
                email_input.send_keys(email)
                email_input.send_keys(Keys.RETURN)

                if not self.handle_email_error():
                    break

            next_prompt = None

            # Check for password or OTC prompt
            try:
                next_prompt = WebDriverWait(self.driver, 60).until(
                    lambda driver: driver.find_element(By.ID, "i0118")
                    if driver.find_elements(By.ID, "i0118")
                    else driver.find_element(By.ID, "idTxtBx_OTC_Password")
                )
            except Exception as e:
                print(f"Error determining login method: {str(e)}")
                self.driver.quit()
                return

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

            self.wait_for_element(By.CLASS_NAME, "css-1dbjc4n", timeout=10)
            print("Login successful")

        except Exception as e:
            print(f"An error occurred during login: {str(e)}")


if __name__ == "__main__":
    skype_login = SkypeLogin()
    skype_login.login()
