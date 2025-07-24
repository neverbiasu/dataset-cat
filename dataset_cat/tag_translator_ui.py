"""
Tag Translator UI Module

This module provides Gradio UI components for the Tag Translator functionality.
"""

import gradio as gr
from typing import Dict, Any
from .tag_translator_api import TagTranslatorAPI
from .tag_translator import TagTranslator


def create_tag_translator_tab_content(locale: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Create the content for the Tag Translator tab.
    
    Args:
        locale (Dict[str, str]): Localization dictionary.
        
    Returns:
        Dict[str, Any]: Dictionary containing all UI components.
    """
    if locale is None:
        locale = {}
    
    # Initialize API
    api = TagTranslatorAPI()
    
    # Get supported sources for the dropdown
    sources_info = api.get_supported_sources()
    booru_sources = sources_info.get("booru_sources", [])
    
    # Create a list of all supported sources (booru + some common non-booru)
    all_sources = booru_sources + ["Zerochan", "Pixiv", "DeviantArt", "ArtStation"]
    
    # Set default value to match the first item in booru_sources (which should be "danbooru")
    default_source = booru_sources[0] if booru_sources else "danbooru"
    
    with gr.Column():
        gr.Markdown(f"### {locale.get('tag_translator_title', '中文标签翻译器')}")
        gr.Markdown(locale.get('tag_translator_desc', '将中文描述翻译为英文标签，并根据数据源类型自动格式化。'))
        
        # Input components
        with gr.Row():
            with gr.Column(scale=3):
                description_input = gr.Textbox(
                    label=locale.get('description_label', '中文描述'),
                    placeholder=locale.get('description_placeholder', '例如：初音未来'),
                    lines=2
                )
            with gr.Column(scale=2):
                source_dropdown = gr.Dropdown(
                    choices=all_sources,
                    value=default_source,
                    label=locale.get('target_source_label', '目标数据源'),
                    info=locale.get('source_info', 'Booru类型源将使用下划线格式')
                )
        
        # Add a dropdown to select translation method
        method_selector = gr.Dropdown(
            choices=["jikan", "googletrans"],
            value="jikan",
            label=locale.get('method_selector_label', '选择翻译方法')
        )

        # Action buttons
        with gr.Row():
            translate_button = gr.Button(
                locale.get('translate_button', '翻译'), 
                variant="primary"
            )
            clear_button = gr.Button(
                locale.get('clear_button', '清空'),
                variant="secondary"
            )
        
        # Output components
        with gr.Row():
            with gr.Column():
                translation_output = gr.Textbox(
                    label=locale.get('translation_output_label', '翻译结果'),
                    interactive=False,
                    lines=2,
                    show_copy_button=True
                )

        # Example section
        with gr.Accordion(locale.get('examples_title', '示例'), open=False):
            gr.Markdown(f"""
            **{locale.get('examples_booru', 'Booru 数据源示例')}:**
            - {locale.get('input_text', '输入')}: 初音未来 → {locale.get('output_text', '输出')}: hatsune_miku
            - {locale.get('input_text', '输入')}: 樱花 → {locale.get('output_text', '输出')}: cherry_blossoms
            
            **{locale.get('examples_other', '其他数据源示例')}:**
            - {locale.get('input_text', '输入')}: 初音未来 → {locale.get('output_text', '输出')}: Hatsune Miku
            - {locale.get('input_text', '输入')}: 樱花 → {locale.get('output_text', '输出')}: Cherry Blossoms
            """)
    
    # Define the translation function
    def translate_description(description: str, source_type: str, method: str) -> tuple:
        """
        Translate the description and return result and status.
        
        Args:
            description (str): Chinese description to translate.
            source_type (str): Target data source type.
            method (str): Translation method (jikan or googletrans).
            
        Returns:
            tuple[str, str]: (translated_result, status_message)
        """
        if not description.strip():
            return "", locale.get('error_empty_description', '请输入要翻译的中文描述')
        
        try:
            # Call the TagTranslator with the selected method
            translator = TagTranslator()
            formatted_tag = translator.translate_to_english(description.strip(), method)

            # Format the tag based on the source type
            formatted_tag = translator.format_tag(formatted_tag, source_type)

            return formatted_tag
            
        except Exception as e:
            return "", f"{locale.get('error_prefix', '错误')}: {str(e)}"
    
    def clear_inputs():
        """Clear all input and output fields."""
        return "", "", ""
    
    # Update the copy function to use JavaScript for clipboard functionality
    def copy_to_clipboard_js():
        return "navigator.clipboard.writeText(document.querySelector('[label=\"翻译结果\"]').value);"

    # Set up event handlers
    translate_button.click(
        fn=translate_description,
        inputs=[description_input, source_dropdown, method_selector],
        outputs=[translation_output]
    )
    
    clear_button.click(
        fn=clear_inputs,
        inputs=[],
        outputs=[description_input, translation_output]
    )
    
    # Return components for external access
    return {
        "description_input": description_input,
        "source_dropdown": source_dropdown,
        "method_selector": method_selector,
        "translate_button": translate_button,
        "clear_button": clear_button,
        "translation_output": translation_output
    }


def update_tag_translator_ui_language(components: Dict[str, Any], locale: Dict[str, str]) -> list:
    """
    Update Tag Translator UI component labels for language switching.
    
    Args:
        components (Dict[str, Any]): Dictionary of UI components.
        locale (Dict[str, str]): Localization dictionary.
        
    Returns:
        list: List of gr.update() calls for each component.
    """
    return [
        gr.update(label=locale.get('description_label', '中文描述'),
                 placeholder=locale.get('description_placeholder', '例如：初音未来')),
        gr.update(label=locale.get('target_source_label', '目标数据源'),
                 info=locale.get('source_info', 'Booru类型源将使用下划线格式')),
        gr.update(label=locale.get('method_selector_label', '选择翻译方法')),
        gr.update(value=locale.get('translate_button', '翻译')),
        gr.update(value=locale.get('clear_button', '清空')),
        gr.update(label=locale.get('translation_output_label', '翻译结果'))
    ]
