"""
Tag Translator UI Module

This module provides Gradio UI components for the Tag Translator functionality.
"""

import gradio as gr
from typing import Dict, Any, List, Optional, Tuple
from .tag_translator_api import TagTranslatorAPI
from .tag_translator import TagTranslator


def _get_supported_sources() -> Tuple[List[str], str]:
    """
    Get supported data sources for the dropdown.
    
    Returns:
        Tuple of (all_sources list, default_source).
    """
    api = TagTranslatorAPI()
    sources_info = api.get_supported_sources()
    booru_sources = sources_info.get("booru_sources", [])
    all_sources = booru_sources + ["Zerochan", "Pixiv", "DeviantArt", "ArtStation"]
    default_source = booru_sources[0] if booru_sources else "danbooru"
    return all_sources, default_source


def _create_translation_handler(locale: Dict[str, str]):
    """
    Create the translation callback function.
    
    Args:
        locale: Localization dictionary.
        
    Returns:
        Callable: The translate_description function.
    """
    def translate_description(description: str, source_type: str, method: str) -> str:
        """Translate the description and return formatted tag."""
        if not description.strip():
            return locale.get("error_empty_description", "请输入要翻译的中文描述")
        
        try:
            translator = TagTranslator()
            formatted_tag = translator.translate_to_english(description.strip(), method)
            formatted_tag = translator.format_tag(formatted_tag, source_type)
            return formatted_tag
        except Exception as e:
            return f"{locale.get('error_prefix', '错误')}: {str(e)}"
    
    return translate_description


def _create_ui_components(
    locale: Dict[str, str],
    all_sources: List[str],
    default_source: str
) -> Dict[str, Any]:
    """
    Create all UI components for the tag translator tab.
    
    Args:
        locale: Localization dictionary.
        all_sources: List of available data sources.
        default_source: Default selected source.
        
    Returns:
        Dictionary of Gradio components.
    """
    gr.Markdown(f"### {locale.get('tag_translator_title', '中文标签翻译器')}")
    gr.Markdown(locale.get("tag_translator_desc", "将中文描述翻译为英文标签，并根据数据源类型自动格式化。"))
    
    with gr.Row():
        with gr.Column(scale=3):
            description_input = gr.Textbox(
                label=locale.get("description_label", "中文描述"),
                placeholder=locale.get("description_placeholder", "例如：初音未来"),
                lines=2
            )
        with gr.Column(scale=2):
            source_dropdown = gr.Dropdown(
                choices=all_sources,
                value=default_source,
                label=locale.get("target_source_label", "目标数据源"),
                info=locale.get("source_info", "Booru类型源将使用下划线格式")
            )
    
    method_selector = gr.Dropdown(
        choices=["jikan", "googletrans"],
        value="jikan",
        label=locale.get("method_selector_label", "选择翻译方法")
    )

    with gr.Row():
        translate_button = gr.Button(
            locale.get("translate_button", "翻译"),
            variant="primary"
        )
        clear_button = gr.Button(
            locale.get("clear_button", "清空"),
            variant="secondary"
        )
    
    with gr.Row():
        with gr.Column():
            translation_output = gr.Textbox(
                label=locale.get("translation_output_label", "翻译结果"),
                interactive=False,
                lines=2,
                show_copy_button=True
            )

    with gr.Accordion(locale.get("examples_title", "示例"), open=False):
        input_text = locale.get("input_text", "输入")
        output_text = locale.get("output_text", "输出")
        gr.Markdown(f"""
        **{locale.get('examples_booru', 'Booru 数据源示例')}:**
        - {input_text}: 初音未来 → {output_text}: hatsune_miku
        - {input_text}: 樱花 → {output_text}: cherry_blossoms
        
        **{locale.get('examples_other', '其他数据源示例')}:**
        - {input_text}: 初音未来 → {output_text}: Hatsune Miku
        - {input_text}: 樱花 → {output_text}: Cherry Blossoms
        """)
    
    return {
        "description_input": description_input,
        "source_dropdown": source_dropdown,
        "method_selector": method_selector,
        "translate_button": translate_button,
        "clear_button": clear_button,
        "translation_output": translation_output
    }


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
    
    all_sources, default_source = _get_supported_sources()
    
    with gr.Column():
        components = _create_ui_components(locale, all_sources, default_source)
    
    # Create handlers
    translate_description = _create_translation_handler(locale)
    
    def clear_inputs():
        """Clear all input and output fields."""
        return "", ""

    # Set up event handlers
    components["translate_button"].click(
        fn=translate_description,
        inputs=[
            components["description_input"],
            components["source_dropdown"],
            components["method_selector"]
        ],
        outputs=[components["translation_output"]]
    )
    
    components["clear_button"].click(
        fn=clear_inputs,
        inputs=[],
        outputs=[components["description_input"], components["translation_output"]]
    )
    
    return components


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
        gr.update(
            label=locale.get("description_label", "中文描述"),
            placeholder=locale.get("description_placeholder", "例如：初音未来")
        ),
        gr.update(
            label=locale.get("target_source_label", "目标数据源"),
            info=locale.get("source_info", "Booru类型源将使用下划线格式")
        ),
        gr.update(label=locale.get("method_selector_label", "选择翻译方法")),
        gr.update(value=locale.get("translate_button", "翻译")),
        gr.update(value=locale.get("clear_button", "清空")),
        gr.update(label=locale.get("translation_output_label", "翻译结果"))
    ]
