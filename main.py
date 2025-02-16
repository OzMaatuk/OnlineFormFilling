# main.py

from dotenv import load_dotenv
from llm_utils.manager import LLMUtils
from playwright.sync_api import sync_playwright
from form_filling.form_filling import FormFilling

def main():
    load_dotenv()
    llm = LLMUtils()
    url = ""
    resume_content = None
    resume_path = "data/personal/resume.pdf"
    
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        
        form_filling = FormFilling(llm, resume_content, resume_path)
        
        # Example of filling an input field
        input_element = page.query_selector("input[type='text']")
        form_filling.fill_input(input_element)
        
        # Example of filling a textarea
        textarea_element = page.query_selector("textarea")
        form_filling.fill_textarea(textarea_element)
        
        # Example of filling a select element
        select_element = page.query_selector("select")
        form_filling.fill_select(select_element)
        
        # Example of filling radio buttons
        radio_elements = page.query_selector_all("input[type='radio']")
        form_filling.fill_radio(radio_elements[0], options=radio_elements)
        
        # Example of handling file upload
        file_input_element = page.query_selector("input[type='file']")
        form_filling.handle_file_upload(page, file_input_element, resume_path)
        
        browser.close()

if __name__ == "__main__":
    main()