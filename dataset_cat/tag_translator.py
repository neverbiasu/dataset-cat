"""
Tag Translator Module

This module provides functionality to translate Chinese descriptions into English tags
and format them according to different data source types (e.g., Booru platforms).
"""

from typing import Dict, List
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
    
    def translate_to_english(self, description: str) -> str:
        """
        Translate Chinese description to English with enhanced error handling.
        
        Args:
            description (str): Chinese description to translate.
            
        Returns:
            str: Translated English text.
            
        Raises:
            Exception: If translation fails.
        """
        try:
            result = self.translator.translate(description, src="zh-cn", dest="en")
            
            # Handle coroutine case for googletrans 4.0.2+
            if hasattr(result, '__await__'):
                import asyncio
                result = asyncio.run(result)
            
            # Validate the result
            if not result.text or result.text.strip() == description.strip():
                raise ValueError("Translation result is invalid or identical to input.")
            
            return result.text
        except Exception as e:
            # Retry with a new translator instance
            try:
                print(f"Retrying translation due to error: {e}")
                from googletrans import Translator
                self.translator = Translator(service_urls=['translate.google.com'])
                result = self.translator.translate(description, src="zh-cn", dest="en")
                
                # Handle coroutine case again
                if hasattr(result, '__await__'):
                    import asyncio
                    result = asyncio.run(result)
                
                # Validate the result
                if not result.text or result.text.strip() == description.strip():
                    raise ValueError("Retry translation result is invalid or identical to input.")
                
                return result.text
            except Exception as retry_error:
                # Log the error and return the original description with a note
                print(f"Translation retry failed: {retry_error}")
                return f"{description} (translation failed)"
    
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
    
    def get_formatted_tag(self, description: str, source_type: str) -> str:
        """
        Translate Chinese description and format it for the specified data source.
        
        Args:
            description (str): Chinese description to translate.
            source_type (str): Target data source type.
            
        Returns:
            str: Formatted English tag ready for use.
            
        Raises:
            Exception: If translation or formatting fails.
        """
        try:
            # Translate the description
            translated_tag = self.translate_to_english(description)
            
            # Format according to source type
            formatted_tag = self.format_tag(translated_tag, source_type)
            
            return formatted_tag
            
        except Exception as e:
            raise Exception(f"Tag processing failed: {str(e)}")


# Convenience function for direct usage
def translate_and_format(description: str, source_type: str) -> str:
    """
    Convenience function to translate and format a tag in one call.
    
    Args:
        description (str): Chinese description to translate.
        source_type (str): Target data source type.
        
    Returns:
        str: Formatted English tag.
    """
    translator = TagTranslator()
    return translator.get_formatted_tag(description, source_type)
