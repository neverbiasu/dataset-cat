"""
Tag Translator Module

This module provides functionality to translate Chinese descriptions into English tags
and format them according to different data source types (e.g., Booru platforms).
"""

from typing import List
from googletrans import Translator


class TagTranslator:
    """
    A class to handle translation of Chinese descriptions to English tags
    and format them based on data source requirements.
    """
    
    # Define Booru-type data sources that require underscore formatting
    BOORU_SOURCES: List[str] = [
        "danbooru",
        "gelbooru", 
        "safebooru",
        "konachan",
        "yande.re"
    ]
    
    def __init__(self) -> None:
        """Initialize the TagTranslator with a Google Translator instance."""
        self.translator = Translator()
    
    def translate_to_english(self, description: str, method: str) -> str:
        """
        Translate Chinese description to English using the specified method.

        Args:
            description (str): Chinese description to translate.
            method (str): The translation method ('jikan' or 'googletrans').

        Returns:
            str: The translated result.
        """
        import requests

        if method == "jikan":
            try:
                # Step 1: Use zhconvert to convert to Traditional Chinese
                zhconvert_url = f"https://api.zhconvert.org/convert?converter=Traditional&text={description}"
                zhconvert_response = requests.get(zhconvert_url)
                zhconvert_data = zhconvert_response.json()

                if zhconvert_data.get("code") == 0:
                    traditional_text = zhconvert_data["data"].get("text", description)
                else:
                    traditional_text = description

                # Step 2: Use jikan to search for anime character information
                jikan_url = f"https://api.jikan.moe/v4/characters?q={traditional_text}"
                jikan_response = requests.get(jikan_url)
                jikan_data = jikan_response.json()

                if "data" in jikan_data and len(jikan_data["data"]) > 0:
                    # Use the first result's English name
                    character_info = jikan_data["data"][0]
                    return character_info.get("name", description)
                else:
                    return f"{traditional_text} (no match found)"

            except Exception as e:
                return f"Error: {e}"

        elif method == "googletrans":
            try:
                # Use googletrans for translation
                result = self.translator.translate(description, src="zh-cn", dest="en")

                # Handle coroutine case for googletrans 4.0.2+
                if hasattr(result, '__await__'):
                    import asyncio
                    result = asyncio.run(result)

                return result.text

            except Exception as e:
                return f"Error: {e}"

        else:
            raise ValueError("Invalid translation method. Choose 'jikan' or 'googletrans'.")
    
    def format_tag(self, tag: str, source_type: str) -> str:
        """
        Format tag based on source type requirements.
        
        Args:
            tag (str): Translated English tag.
            source_type (str): Data source type (e.g., "Danbooru", "Zerochan").
            
        Returns:
            str: Formatted tag according to source requirements.
        """
        if source_type.lower() in self.BOORU_SOURCES:
            # Booru platforms use lowercase with underscores
            return tag.replace(" ", "_").lower()
        else:
            # Other platforms keep original capitalization and spaces
            return tag
    
    def get_formatted_tag(self, description: str, source_type: str, method: str = "googletrans") -> str:
        """
        Translate Chinese description and format it for the specified data source.
        
        Args:
            description (str): Chinese description to translate.
            source_type (str): Target data source type.
            method (str): Translation method, defaults to "googletrans".
            
        Returns:
            str: Formatted English tag ready for use.
            
        Raises:
            ValueError: If translation or formatting fails.
        """
        try:
            # Translate the description with the specified method
            translated_tag = self.translate_to_english(description, method)
            
            # Format according to source type
            formatted_tag = self.format_tag(translated_tag, source_type)
            
            return formatted_tag
            
        except ValueError as e:
            raise ValueError(f"Tag processing failed: {str(e)}")
    
    def translate_description(self, description: str, source_type: str, method: str) -> List[str]:
        """
        Translate a description and format it based on the selected method.

        Args:
            description (str): The Chinese description to translate.
            source_type (str): The target data source type.
            method (str): The translation method ('jikan' or 'googletrans').

        Returns:
            List[str]: A list containing the formatted tag, the translation method used, and a success message.
        """
        translated_tag = self.translate_to_english(description, method)
        formatted_tag = self.format_tag(translated_tag, source_type)
        return [formatted_tag, method, "Translation successful! (Booru format: lowercase + underscore)"]


# Convenience function for direct usage
def translate_and_format(description: str, source_type: str, method: str = "googletrans") -> str:
    """
    Convenience function to translate and format a tag in one call.
    
    Args:
        description (str): Chinese description to translate.
        source_type (str): Target data source type.
        method (str): Translation method, defaults to "googletrans".
        
    Returns:
        str: Formatted English tag.
    """
    translator = TagTranslator()
    return translator.get_formatted_tag(description, source_type, method)
