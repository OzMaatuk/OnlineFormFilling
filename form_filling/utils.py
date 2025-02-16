# src\utils.py

from llm_utils import LLMUtils
import pypdf

class GenerateContentUtils:
    def __init__(self, llm: LLMUtils = None, resume_content: str = None, resume_path: str = None):
        if llm == None:
            llm = LLMUtils()
        self.llm = llm
        if resume_path:
            self.resume_content = self.pdf_to_text(resume_path)
        else:
            self.resume_content = resume_content

    def generate_field_content(self, field_label, resume_content: str = None) -> str:
        if resume_content is None:
            resume_content = self.resume_content
        instructions = f"""
            Following the resume below, return the answer for the following question: {field_label}
            \n resume: {resume_content} \n
            give positive answer as I want to get the interview for the job.
            if its numeric, return only the number.
            if its yes / no quesion, return only yes or no.
            and for any other question, be specific and return only necessary details.
        """
        return self.llm.generate_text(instructions)

    def generate_radio_content(self, option_labels: list, resume_content: str = None) -> str:
        if resume_content is None:
            resume_content = self.resume_content
        instructions = f"""
            Following the resume below, choose the right option: {option_labels}
            \n resume: {resume_content} \n
            be positive as I want to get the interview for the job.
            return only the text of the selected option and nothing else.
        """
        return self.llm.generate_text(instructions)

    def generate_select_content(self, options: list, resume_content: str = None) -> str:
        if resume_content is None:
            resume_content = self.resume_content
        instructions = f"""
            Following the resume below, select the right option: {options}
            \n resume: {resume_content} \n
            be positive as I want to get the interview for the job.
            return only the text of the selected option and nothing else. 
        """
        return self.llm.generate_text(instructions)

    @staticmethod
    def pdf_to_text(pdf_path: str) -> str:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.get_page(page_num)
                text += page.extract_text()
        return text