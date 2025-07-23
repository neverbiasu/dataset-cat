"""
Tag Translator API

This module provides API interfaces for the Tag Translator functionality.
"""

from typing import Dict, Any
from .tag_translator import TagTranslator


class TagTranslatorAPI:
    """
    API interface for Tag Translator functionality.
    """
    
    def __init__(self) -> None:
        """Initialize the API with a TagTranslator instance."""
        self.translator = TagTranslator()
    
    def translate_tag(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        API endpoint to translate and format tags.
        
        Args:
            request_data (Dict[str, Any]): Request containing:
                - description (str): Chinese description
                - source_type (str): Data source type
                
        Returns:
            Dict[str, Any]: Response containing:
                - formatted_tag (str): Processed tag
                - success (bool): Operation status
                - error (str, optional): Error message if failed
        """
        try:
            # Validate input
            if "description" not in request_data:
                return {
                    "success": False,
                    "error": "Missing required field: description"
                }
            
            if "source_type" not in request_data:
                return {
                    "success": False,
                    "error": "Missing required field: source_type"
                }
            
            description = request_data["description"]
            source_type = request_data["source_type"]
            
            # Validate input types
            if not isinstance(description, str) or not description.strip():
                return {
                    "success": False,
                    "error": "Description must be a non-empty string"
                }
            
            if not isinstance(source_type, str) or not source_type.strip():
                return {
                    "success": False,
                    "error": "Source type must be a non-empty string"
                }
            
            # Process the request
            formatted_tag = self.translator.get_formatted_tag(description, source_type)
            
            return {
                "success": True,
                "formatted_tag": formatted_tag
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_sources(self) -> Dict[str, Any]:
        """
        Get list of supported data sources and their formatting rules.
        
        Returns:
            Dict[str, Any]: Information about supported sources.
        """
        return {
            "success": True,
            "booru_sources": self.translator.BOORU_SOURCES,
            "formatting_rules": {
                "booru": "Lowercase with underscores (e.g., hatsune_miku)",
                "other": "Original capitalization with spaces (e.g., Hatsune Miku)"
            }
        }


# Convenience functions for direct API usage
def translate_tag_request(description: str, source_type: str) -> Dict[str, Any]:
    """
    Convenience function for tag translation requests.
    
    Args:
        description (str): Chinese description to translate.
        source_type (str): Target data source type.
        
    Returns:
        Dict[str, Any]: API response with formatted tag or error.
    """
    api = TagTranslatorAPI()
    request_data = {
        "description": description,
        "source_type": source_type
    }
    return api.translate_tag(request_data)


def get_supported_sources() -> Dict[str, Any]:
    """
    Convenience function to get supported data sources.
    
    Returns:
        Dict[str, Any]: Information about supported sources.
    """
    api = TagTranslatorAPI()
    return api.get_supported_sources()
