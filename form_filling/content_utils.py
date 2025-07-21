# form_filling/content_utils.py

from typing import Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
import pypdf
import logging

# Set up logger
logger = logging.getLogger(__name__)

class GenerateContentUtils:
    def __init__(self, llm: Optional[BaseChatModel] = None, resume_content: Optional[str] = None, 
                 resume_path: Optional[str] = None, chat_model_config: Optional[dict] = None):
        self.llm: Optional[BaseChatModel] = llm if llm is not None else init_chat_model(**(chat_model_config or {}))
        if resume_path:
            logger.info(f"Loading resume content from file: {resume_path}")
            self.resume_content: Optional[str] = self.pdf_to_text(resume_path)
        else:
            logger.info("Using provided resume content")
            self.resume_content: Optional[str] = resume_content

    def generate_field_content(self, field_label: str, resume_content: Optional[str] = None) -> str:
        """Generate appropriate content for a text field based on the resume"""
        if resume_content is None:
            resume_content = self.resume_content
        logger.debug(f"Generating content for field: {field_label}")
        instructions = f"""
            Following the resume below, return the answer for the following question: {field_label}
            \n resume: {resume_content} \n
            give positive answer as I want to get the interview for the job.
            if its numeric, return only the number.
            if its yes / no quesion, return only yes or no.
            and for any other question, be specific and return only necessary details.
        """
        if self.llm is not None and hasattr(self.llm, "invoke"):
            response_obj = self.llm.invoke(instructions)
            response = getattr(response_obj, "content", str(response_obj))
        else:
            logger.error("LLM is not initialized or does not have 'invoke' method.")
            response = ""
        logger.debug(f"Generated content for '{field_label}': {response[:50]}...")
        return response

    def generate_radio_content(self, option_labels: List[str], resume_content: Optional[str] = None) -> str:
        """Generate appropriate selection for radio buttons based on resume"""
        if resume_content is None:
            resume_content = self.resume_content
        # Filter out None values
        option_labels_filtered: List[str] = [label for label in option_labels if label is not None]
        logger.debug(f"Generating radio selection from options: {option_labels_filtered}")
        instructions = f"""
            Following the resume below, choose the right option: {option_labels_filtered}
            \n resume: {resume_content} \n
            be positive as I want to get the interview for the job.
            return only the text of the selected option and nothing else.
        """
        if self.llm is not None and hasattr(self.llm, "invoke"):
            response_obj = self.llm.invoke(instructions)
            response = getattr(response_obj, "content", str(response_obj))
        else:
            logger.error("LLM is not initialized or does not have 'invoke' method.")
            response = ""
        logger.info(f"Selected radio option: {response}")
        return response

    def generate_select_content(self, options: List[str], resume_content: Optional[str] = None) -> str:
        """Generate appropriate selection for dropdown based on resume"""
        if resume_content is None:
            resume_content = self.resume_content
        # Filter out None values
        options_filtered: List[str] = [opt for opt in options if opt is not None]
        logger.debug(f"Generating select option from choices: {options_filtered}")
        instructions = f"""
            Following the resume below, select the right option: {options_filtered}
            \n resume: {resume_content} \n
            be positive as I want to get the interview for the job.
            return only the text of the selected option and nothing else. 
        """
        if self.llm is not None and hasattr(self.llm, "invoke"):
            response_obj = self.llm.invoke(instructions)
            response = getattr(response_obj, "content", str(response_obj))
        else:
            logger.error("LLM is not initialized or does not have 'invoke' method.")
            response = ""
        logger.info(f"Selected dropdown option: {response}")
        return response

    @staticmethod
    def pdf_to_text(pdf_path: str) -> str:
        """Extract text content from a PDF file"""
        logger.info(f"Converting PDF to text: {pdf_path}")
        try:
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ""
                page_count = len(reader.pages)
                logger.debug(f"PDF has {page_count} pages")
                for page_num in range(page_count):
                    page = reader.get_page(page_num)
                    text += page.extract_text()
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise

    def set_new_resume_from_path(self, resume_path: str):
        self.resume_content = self.pdf_to_text(resume_path)

    def set_new_resume(self, resume_content: str):
        self.resume_content = resume_content