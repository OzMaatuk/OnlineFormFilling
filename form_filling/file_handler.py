# form_filling/file_handler.py

import logging
from typing import Optional
from playwright.sync_api import Page, ElementHandle

logger = logging.getLogger(__name__)

class FileHandler:
    
    def handle_file_upload(self, page: Page, element: ElementHandle, 
                           resume_path: Optional[str]) -> None:
        """Handle file upload interactions"""
        if not resume_path:
            logger.warning(f"No file path provided for file upload")
            return
            
        logger.debug(f"Handling file upload for path '{resume_path}'")
        try:
            with page.expect_file_chooser() as fc_info:
                element.click(force=True)
            file_chooser = fc_info.value
            file_chooser.set_files(resume_path)
            logger.info(f"Successfully uploaded file '{resume_path}'")
        except Exception as e:
            logger.error(f"Failed to upload file '{resume_path}': {e}")
            raise