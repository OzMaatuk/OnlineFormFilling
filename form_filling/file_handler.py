# form_filling/file_handler.py

import logging
from playwright.sync_api import Page, ElementHandle

logger = logging.getLogger(__name__)

class FileHandler:
    
    def handle_file_upload(self, page: Page, element: ElementHandle, resume_path: str) -> None:
        """Handle file upload interactions"""
        if not resume_path:
            logger.warning(f"No file path provided for file upload")
            return
            
        logger.debug(f"Handling file upload for path '{resume_path}'")
        with page.expect_file_chooser() as fc_info:
            element.click()
        file_chooser = fc_info.value
        file_chooser.set_files(resume_path)
        logger.info(f"Uploaded file '{resume_path}'")