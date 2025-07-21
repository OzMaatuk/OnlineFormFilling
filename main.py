# main.py

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from langchain.chat_models import init_chat_model
from form_filling.form_filling import FormFilling

def main():
    load_dotenv()
    # Use Ollama Mistral model with temperature=0, following LangChain API
    llm = init_chat_model(
        model="mistral",           # Model name
        model_provider="ollama",   # Provider
        temperature=0              # Model temperature
    )
    url = "https://www.comeet.com/jobs/crossriver/C7.00F/would-love-to-join-cross-river/92.F23"
    # url = "https://careers.checkpoint.com/index.php?m=cpcareers&a=show&joborderid=20816&source=51&mode=clear"
    resume_content = None
    resume_path = "data/personal/resume.pdf"

    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        form_filling = FormFilling(llm, resume_content, resume_path)

        # page.query_selector("button:has-text('Apply')").click()

        # Example of filling an input field
        input_elements_ids = ["firstName", "lastName", "email"]
        input_elements = page.query_selector_all("input[type='text']")
        if input_elements:
            for input_element in input_elements:
                try:
                    element_id = input_element.get_attribute("id")
                    if any(id_part in element_id for id_part in input_elements_ids):
                        form_filling.fill_element(input_element, element_id)
                except Exception as e:
                    print(e)

        # Example of filling a textarea
        textarea_elements_ids = ["personal"]
        textarea_elements = page.query_selector_all("textarea")
        if textarea_elements:
            for textarea_element in textarea_elements:
                try:
                    element_id = textarea_element.get_attribute("id")
                    if any(id_part in element_id for id_part in textarea_elements_ids):
                        form_filling.fill_element(textarea_element, element_id)
                except Exception as e:
                    print(e)

        # Example of filling a select element
        select_elements_ids = ["experience", "education"]
        select_elements = page.query_selector_all("select")
        if select_elements:
            for select_element in select_elements:
                try:
                    element_id = select_element.get_attribute("id")
                    if any(id_part in element_id for id_part in select_elements_ids):
                        form_filling.fill_element(select_element, element_id)
                except Exception as e:
                    print(e)

        # Example of filling radio buttons
        radio_elements_ids = ["gender", "availability"]
        radio_elements = page.query_selector_all("[role='radiogroup']")
        if radio_elements:
            for radio_element in radio_elements:
                try:
                    element_id = radio_element.get_attribute("id")
                    if any(id_part in element_id for id_part in radio_elements_ids):
                        form_filling.fill_element(radio_element, element_id)
                except Exception as e:
                    print(e)

        # Example of handling file upload
        file_input_elements_ids = ["resume", "coverLetter"]
        file_input_elements = page.query_selector_all("input[type='file']")
        if file_input_elements:
            for file_input_element in file_input_elements:
                try:
                    element_id = file_input_element.get_attribute("id")
                    if any(id_part in element_id for id_part in file_input_elements_ids):
                        form_filling.handle_file_upload(page, file_input_element, resume_path, element_id)
                except Exception as e:
                    print(e)

        browser.close()

if __name__ == "__main__":
    main()