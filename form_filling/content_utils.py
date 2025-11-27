# form_filling/content_utils.py

from typing import Optional, List, Union
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import init_chat_model
import pypdf
import logging
import os.path
from pathvalidate import is_valid_filepath

logger = logging.getLogger(__name__)


class GenerateContentUtils:
    def __init__(
        self,
        llm: Optional[Union[BaseChatModel, dict]] = None,
        resume: Optional[str] = None,
    ):
        """Initialize content utilities with Langchain chat model and resume content"""
        logger.info("Initialize GenerateContentUtils")

        # self.llm: Optional[BaseChatModel]  # Attribute annotation for type checkers
        if isinstance(llm, dict):
            self.llm = init_chat_model(**(llm or {}))
        elif isinstance(llm, BaseChatModel):
            self.llm = llm
        elif llm is None:
            self.llm = None
        else:
            raise ValueError(
                f"LLM must be a BaseChatModel instance, a configuration dictionary, or None. llm: {llm}"
            )

        self.resume_content: str = GenerateContentUtils.set_new_resume(resume)
        logger.debug("GenerateContentUtils Initialized")

    def generate_field_content(
        self, field_label: str, resume_content: Optional[str] = None
    ) -> str:
        """Generate appropriate content for a text field based on the resume"""
        if resume_content is None:
            resume_content = self.resume_content
        logger.debug(f"Generating content for field: {field_label}")
        instructions = f"""
            Following the resume below, return the answer for the following question: {field_label}
            \n resume: {resume_content} \n
            give positive answer as I want to get the interview for the job.
            if its \"yes / no\" quesion, return only yes or no.
            if its \"how many\"  question or any request for numeric response, return only number.
            if its simple personal info like \"name\", \"email\", \"phone number\", \"address\", \"linkedin\", \"github\", etc., return only that info. onlt the exact value to be filled.
            and for any other question, be specific and return only necessary details to be filled.
        """
        if self.llm is not None and hasattr(self.llm, "invoke"):
            response_obj = self.llm.invoke(instructions)
            response = getattr(response_obj, "content", str(response_obj))
        else:
            logger.error("LLM is not initialized or does not have 'invoke' method.")
            response = ""
        logger.debug(f"Generated content for '{field_label}': {response[:50]}...")
        return response

    def generate_radio_content(
        self, option_labels: List[str], resume_content: Optional[str] = None
    ) -> str:
        """Generate appropriate selection for radio buttons based on resume"""
        if resume_content is None:
            resume_content = self.resume_content
        # Filter out None values
        option_labels_filtered: List[str] = [
            label for label in option_labels if label is not None
        ]
        logger.debug(
            f"Generating radio selection from options: {option_labels_filtered}"
        )
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

    def generate_select_content(
        self, options: List[str], resume_content: Optional[str] = None
    ) -> str:
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
            with open(pdf_path, "rb") as file:
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

    @staticmethod
    def set_new_resume(resume: Optional[str]) -> str:
        if isinstance(resume, str):
            if is_valid_filepath(resume):
                if not os.path.exists(resume):
                    raise ValueError(f"Resume file path is invalid: {resume}")
                logger.debug(f"Loading resume content from file: {resume}")
                resume = GenerateContentUtils.pdf_to_text(resume)
            else:
                logger.debug("Using provided resume content")
            return resume
        else:
            raise ValueError(
                f"Resume must be a valid file path or string content, resume: {resume}"
            )
