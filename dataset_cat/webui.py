import logging
import os
import json
from pathlib import Path
from typing import Optional

import gradio as gr

from dataset_cat.crawler import Crawler
from dataset_cat.postprocessing_ui import create_postprocessing_tab_content, update_postprocessing_ui_language
from dataset_cat.tag_translator_ui import create_tag_translator_tab_content, update_tag_translator_ui_language
from waifuc.action import FilterSimilarAction, NoMonochromeAction
from waifuc.export import HuggingFaceExporter, SaveExporter, TextualInversionExporter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for data sources
ANIME_PICTURES_BROKEN = "AnimePictures (Broken)"

# Define size options for each data source
# These are example values and might need adjustment based on actual source capabilities
SIZE_OPTIONS_MAP = {
    "Danbooru": ["Original", "Large (2000px+)", "Medium (1000-1999px)", "Small (<1000px)"],
    "Zerochan": ["full", "large", "medium"],  # Zerochan valid select options: full, large, medium
    "Safebooru": ["Original", "Large", "Medium", "Small"],
    "Gelbooru": ["Original", "Large", "Medium", "Small"],
    "WallHaven": [
        "Original",
        "1920x1080",
        "2560x1440",
        "3840x2160",
        "Custom",
    ],  # Wallhaven supports various resolutions
    "Konachan": ["Original", "Large", "Medium", "Small"],
    "KonachanNet": ["Original", "Large", "Medium", "Small"],
    "Lolibooru": ["Original", "Large", "Medium", "Small"],
    "Yande": ["Original", "Large", "Medium", "Small"],
    "Rule34": ["Original", "Large", "Medium", "Small"],
    "HypnoHub": ["Original", "Large", "Medium", "Small"],
    "Paheal": ["Original", "Large", "Medium", "Small"],
    ANIME_PICTURES_BROKEN: [],  # No options for broken source
    "Duitang": ["Original", "Large", "Medium", "Small"],  # Duitang is more about collections
    "Pixiv": ["original", "large", "medium", "square_medium"],
    "Derpibooru": ["full", "large", "medium", "small", "thumb"],
}

DEFAULT_SIZE_MAP = {
    "Danbooru": "Original",
    "Zerochan": "large",  # Zerochan default select is 'large', not 'Original'
    "Safebooru": "Original",
    "Gelbooru": "Original",
    "WallHaven": "Original",
    "Konachan": "Original",
    "KonachanNet": "Original",
    "Lolibooru": "Original",
    "Yande": "Original",
    "Rule34": "Original",
    "HypnoHub": "Original",
    "Paheal": "Original",
    ANIME_PICTURES_BROKEN: None,
    "Duitang": "Original",
    "Pixiv": "large",
    "Derpibooru": "large",
}

# 数据源列表
SOURCE_LIST = [
    "Danbooru",
    "Zerochan",
    "Safebooru",
    "Gelbooru",
    "WallHaven",
    "Konachan",
    "KonachanNet",
    "Lolibooru",
    "Yande",
    "Rule34",
    "HypnoHub",
    "Paheal",
    ANIME_PICTURES_BROKEN,  # Marked as broken
    "Duitang",
    "Pixiv",
    "Derpibooru",
]


# 更新数据源选择函数
def get_sources():
    return Crawler.get_sources()


# 更新爬取任务函数
def start_crawl(source_name, tags, limit, size, strict):
    return Crawler.start_crawl(source_name, tags, limit, size, strict)


# 数据处理函数
def apply_actions(source, actions):
    if "NoMonochrome" in actions and hasattr(source, "attach"):
        source = source.attach(NoMonochromeAction())
    if "FilterSimilar" in actions and hasattr(source, "attach"):
        source = source.attach(FilterSimilarAction())
    return source


# Author extractor functions for different data sources
def _extract_danbooru_author(meta: dict) -> Optional[str]:
    """Extract author from Danbooru metadata.
    
    Args:
        meta: Metadata dictionary from ImageItem.
        
    Returns:
        Author name or None if not found.
    """
    danbooru_data = meta.get("danbooru", {})
    if not danbooru_data:
        return None
    
    # Try tag_string_artist first
    artists = danbooru_data.get("tag_string_artist", "").strip()
    if artists:
        return artists.replace(" ", ", ")
    
    # Try tags.artist
    tags = danbooru_data.get("tags", {})
    if isinstance(tags, dict):
        artist_list = tags.get("artist", [])
        if artist_list and isinstance(artist_list, list):
            return ", ".join(artist_list)
    
    return None


def _extract_safebooru_author(meta: dict) -> Optional[str]:
    """Extract author from Safebooru metadata.
    
    Args:
        meta: Metadata dictionary from ImageItem.
        
    Returns:
        Author name or None if not found.
    """
    safebooru_data = meta.get("safebooru", {})
    if not safebooru_data:
        return None
    
    artists = safebooru_data.get("tag_string_artist", "").strip()
    return artists.replace(" ", ", ") if artists else None


def _extract_zerochan_author(meta: dict) -> Optional[str]:
    """Extract author from Zerochan metadata.
    
    Args:
        meta: Metadata dictionary from ImageItem.
        
    Returns:
        Author name or None if not found.
    """
    zerochan_data = meta.get("zerochan", {})
    if not zerochan_data:
        return None
    
    # Direct author fields
    for field in ("author", "uploader"):
        value = zerochan_data.get(field)
        if value:
            return str(value)
    
    # Infer from tags
    tags = zerochan_data.get("tags", [])
    if isinstance(tags, list):
        for tag in reversed(tags):
            if tag.isalpha() and tag.islower() and 2 <= len(tag) <= 20:
                return tag
    
    return None


def _extract_pixiv_author(meta: dict) -> Optional[str]:
    """Extract author from Pixiv metadata.
    
    Args:
        meta: Metadata dictionary from ImageItem.
        
    Returns:
        Author name or None if not found.
    """
    pixiv_data = meta.get("pixiv", {})
    if not pixiv_data:
        return None
    
    user_data = pixiv_data.get("user", {})
    if isinstance(user_data, dict):
        for field in ("name", "account"):
            value = user_data.get(field)
            if value:
                return str(value)
    
    return None


def _extract_gelbooru_author(meta: dict) -> Optional[str]:
    """Extract author from Gelbooru metadata.
    
    Args:
        meta: Metadata dictionary from ImageItem.
        
    Returns:
        Author name or None if not found.
    """
    import re
    
    gelbooru_data = meta.get("gelbooru", {})
    if not gelbooru_data:
        return None
    
    tags = gelbooru_data.get("tags", "")
    match = re.search(r"artist:(\w+)", str(tags))
    return match.group(1) if match else None


def _extract_generic_author(meta: dict) -> Optional[str]:
    """Extract author from generic metadata fields.
    
    Args:
        meta: Metadata dictionary from ImageItem.
        
    Returns:
        Author name or None if not found.
    """
    # Try generic tags
    tags = meta.get("tags", {})
    if isinstance(tags, dict):
        for tag in tags:
            if "artist:" in tag:
                return tag.replace("artist:", "")
            if any(k in tag.lower() for k in ("creator", "author", "artist")):
                return tag
    
    # Fallback: search all source data for 'author' field
    for source_data in meta.values():
        if isinstance(source_data, dict) and "author" in source_data:
            author = source_data["author"]
            if author and str(author).strip():
                return str(author).strip()
    
    return None


# List of author extractors in priority order
_AUTHOR_EXTRACTORS = [
    _extract_danbooru_author,
    _extract_safebooru_author,
    _extract_zerochan_author,
    _extract_pixiv_author,
    _extract_gelbooru_author,
    _extract_generic_author,
]


# 作者信息提取函数
def extract_author_info(item) -> str:
    """Extract author information from different data sources.

    Args:
        item: ImageItem from waifuc containing metadata.

    Returns:
        Author name or "Unknown" if not found.
    """
    meta = item.meta
    logger.info(f"Extracting author info, meta keys: {list(meta.keys())}")
    
    for extractor in _AUTHOR_EXTRACTORS:
        result = extractor(meta)
        if result:
            return result
    
    logger.info("No author info found, return 'Unknown'")
    return "Unknown"


# 导出函数
def export_data(source, output_dir, save_meta, save_author, exporter_type, hf_repo=None, hf_token=None, locale=None):
    if locale is None:
        locale = {}
    if exporter_type == "SaveExporter":
        exporter = SaveExporter(
            output_dir=output_dir,
            no_meta=not save_meta,
            save_params={"format": "PNG"},
        )
    elif exporter_type == "TextualInversionExporter":
        exporter = TextualInversionExporter(
            output_dir=output_dir,
            clear=True,
        )
    elif exporter_type == "HuggingFaceExporter":
        if not hf_repo or not hf_token:
            return locale.get("hf_exporter_requires", "HuggingFaceExporter requires 'hf_repo' and 'hf_token'.")
        exporter = HuggingFaceExporter(
            repository=hf_repo,
            hf_token=hf_token,
            repo_type="dataset",
        )
    else:
        return locale.get("unsupported_exporter", "Unsupported exporter type: {exporter_type}").format(exporter_type=exporter_type)
    logger.info(f"Exporting data, save_author={save_author}")
    for item in source:
        exporter.export_item(item)
        if save_author:
            author = extract_author_info(item)
            image_name = item.meta.get("filename", "unknown")
            if "." in image_name:
                image_name_no_ext = image_name.rsplit(".", 1)[0]
            else:
                image_name_no_ext = image_name
            author_file_path = f"{output_dir}/{image_name_no_ext}_author.txt"
            try:
                with open(author_file_path, "w", encoding="utf-8") as author_file:
                    author_file.write(f"Author: {author}\n")
                logger.info(f"Saved author info to: {author_file_path}")
            except Exception as e:
                logger.error(f"Failed to save author info: {e}")
    return locale.get("data_exported_success", "Data exported successfully.")


# Load locales
def load_locales() -> dict:
    """
    Load localization data from JSON files.

    Returns:
        Dict[str, dict]: Dictionary of language codes to locale data.
    """
    locales = {}
    locale_dir = Path(__file__).parent / "locales"
    if not locale_dir.exists():
        logger.warning(f"Locales directory not found: {locale_dir}")
        return {"en": {}, "zh": {}}
    
    for locale_file in locale_dir.glob("*.json"):
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
                lang_code = locale_file.stem
                locales[lang_code] = locale_data
                logger.info(f"Loaded locale: {lang_code}")
        except Exception as e:
            logger.error(f"Failed to load locale {locale_file}: {e}")
    
    if not locales:
        logger.warning("No locales found, using defaults")
        return {"en": {}, "zh": {}}
    
    return locales


def _create_process_data_handler(locales: dict):
    """
    Create the data processing callback function.
    
    Args:
        locales: Dictionary of locale data.
        
    Returns:
        Callable: The process_data function.
    """
    def process_data(
        source_name: str,
        tags: str,
        limit: int,
        size: str,
        strict: bool,
        actions: list,
        output_dir: str,
        save_meta: bool,
        save_author: bool,
        exporter_type: str,
        hf_repo: str,
        hf_token: str,
        lang: str
    ) -> str:
        """Process data from the selected source."""
        logger.info("Start processing data...")
        locale_data = locales.get(lang, locales.get("zh", {}))
        source, message = start_crawl(source_name, tags, limit, size, strict)
        if source is None:
            logger.error(f"Crawl failed: {message}")
            return message
        source = apply_actions(source, actions)
        result = export_data(
            source, output_dir, save_meta, save_author,
            exporter_type, hf_repo, hf_token, locale_data
        )
        logger.info(f"Process finished: {result}")
        return result
    return process_data


def _create_crawl_tab_components() -> dict:
    """
    Create UI components for the crawl tab.
    
    Returns:
        dict: Dictionary of Gradio components.
    """
    available_sources = get_sources()
    default_source = available_sources[0] if available_sources else None
    
    components = {
        "src_dropdown": gr.Dropdown(
            choices=available_sources,
            value=default_source,
            label="数据源"
        ),
        "tags_input": gr.Textbox(label="标签（逗号分隔）"),
        "limit_slider": gr.Slider(1, 350, value=10, step=1, label="数量限制"),
        "size_dropdown": gr.Dropdown(
            choices=SIZE_OPTIONS_MAP.get(default_source, []),
            value=None,
            label="图片尺寸"
        ),
        "strict_checkbox": gr.Checkbox(label="严格模式（仅 Zerochan）"),
        "actions_group": gr.CheckboxGroup(["NoMonochrome", "FilterSimilar"], label="操作"),
        "output_dir_input": gr.Textbox(value="./output", label="输出目录"),
        "save_meta_checkbox": gr.Checkbox(label="保存元数据"),
        "save_author_checkbox": gr.Checkbox(label="保存作者信息", value=True),
        "exporter_dropdown": gr.Dropdown(
            ["SaveExporter", "TextualInversionExporter", "HuggingFaceExporter"],
            value="SaveExporter",
            label="导出器类型"
        ),
        "hf_repo_input": gr.Textbox(label="HuggingFace 仓库（可选）"),
        "hf_token_input": gr.Textbox(label="HuggingFace Token（可选）", type="password"),
        "result_output": gr.Textbox(label="结果", interactive=False),
        "start_button": gr.Button("开始"),
    }
    return components


def _get_crawl_tab_language_updates(locale_data: dict) -> list:
    """
    Generate language update objects for crawl tab components.
    
    Args:
        locale_data: Dictionary of localized strings.
        
    Returns:
        list: List of gr.update() objects.
    """
    return [
        gr.update(label=locale_data.get("data_source_label", "数据源")),
        gr.update(label=locale_data.get("tags_label", "标签（逗号分隔）")),
        gr.update(label=locale_data.get("limit_label", "数量限制")),
        gr.update(label=locale_data.get("image_size_label", "图片尺寸")),
        gr.update(label=locale_data.get("strict_mode_label", "严格模式（仅 Zerochan）")),
        gr.update(label=locale_data.get("actions_label", "操作")),
        gr.update(label=locale_data.get("output_directory_label", "输出目录")),
        gr.update(label=locale_data.get("save_metadata_label", "保存元数据")),
        gr.update(label=locale_data.get("save_author_label", "保存作者信息")),
        gr.update(label=locale_data.get("exporter_type_label", "导出器类型")),
        gr.update(label=locale_data.get("hf_repo_label", "HuggingFace 仓库（可选）")),
        gr.update(label=locale_data.get("hf_token_label", "HuggingFace Token（可选）")),
        gr.update(value=locale_data.get("start_button", "开始")),
        gr.update(label=locale_data.get("result_label", "结果")),
    ]


def _create_language_switch_handler(
    locales: dict,
    postproc_components: dict,
    tag_translator_components: dict
):
    """
    Create the language switch callback function.
    
    Args:
        locales: Dictionary of locale data.
        postproc_components: Post-processing UI components.
        tag_translator_components: Tag translator UI components.
        
    Returns:
        Callable: The switch_language function.
    """
    def switch_language(lang: str) -> list:
        """Switch UI language."""
        locale_data = locales.get(lang, {})
        title_text = f"# {locale_data.get('app_title', '数据猫 WebUI')}"
        
        # Base updates for header
        updates = [
            lang,
            gr.update(value=title_text),
            gr.update(label=locale_data.get("language_selector", "语言/Language")),
        ]
        
        # Crawl tab updates
        updates.extend(_get_crawl_tab_language_updates(locale_data))
        
        # Post-processing UI updates
        post_updates = update_postprocessing_ui_language(postproc_components, locale_data)
        
        # Tag translator UI updates
        tag_translator_updates = update_tag_translator_ui_language(
            tag_translator_components, locale_data
        )
        
        return updates + post_updates + tag_translator_updates
    
    return switch_language


def _get_crawl_tab_inputs(crawl_components: dict, current_lang) -> list:
    """Build input list for crawl tab processing.
    
    Args:
        crawl_components: Dictionary of crawl tab components.
        current_lang: Current language state component.
        
    Returns:
        List of input components.
    """
    return [
        crawl_components["src_dropdown"],
        crawl_components["tags_input"],
        crawl_components["limit_slider"],
        crawl_components["size_dropdown"],
        crawl_components["strict_checkbox"],
        crawl_components["actions_group"],
        crawl_components["output_dir_input"],
        crawl_components["save_meta_checkbox"],
        crawl_components["save_author_checkbox"],
        crawl_components["exporter_dropdown"],
        crawl_components["hf_repo_input"],
        crawl_components["hf_token_input"],
        current_lang,
    ]


def _get_language_switch_outputs(
    current_lang,
    title,
    language_selector,
    crawl_components: dict,
    postproc_components: dict,
    tag_translator_components: dict
) -> list:
    """Build output list for language switching.
    
    Args:
        current_lang: Current language state component.
        title: Title component.
        language_selector: Language selector component.
        crawl_components: Dictionary of crawl tab components.
        postproc_components: Dictionary of post-processing components.
        tag_translator_components: Dictionary of tag translator components.
        
    Returns:
        List of output components.
    """
    return [
        current_lang,
        title,
        language_selector,
        crawl_components["src_dropdown"],
        crawl_components["tags_input"],
        crawl_components["limit_slider"],
        crawl_components["size_dropdown"],
        crawl_components["strict_checkbox"],
        crawl_components["actions_group"],
        crawl_components["output_dir_input"],
        crawl_components["save_meta_checkbox"],
        crawl_components["save_author_checkbox"],
        crawl_components["exporter_dropdown"],
        crawl_components["hf_repo_input"],
        crawl_components["hf_token_input"],
        crawl_components["start_button"],
        crawl_components["result_output"],
    ] + list(postproc_components.values()) + list(tag_translator_components.values())


# WebUI 启动函数
def launch_webui(
    host: str = "0.0.0.0",
    port: int = 7860,
    debug: bool = False,
    share: bool = False
) -> None:
    """Launch the Dataset Cat WebUI application.
    
    Args:
        host: Host address to bind the server to.
        port: Port number to run the server on.
        debug: Whether to enable debug mode.
        share: Whether to create a public Gradio share link.
    """
    locales = load_locales()
    process_data = _create_process_data_handler(locales)
    
    with gr.Blocks(css="footer {visibility: hidden}") as demo:
        current_lang = gr.State("zh")
        title = gr.Markdown("# 数据猫 WebUI")
        language_selector = gr.Radio(
            choices=list(locales.keys()),
            value="zh",
            label="语言/Language"
        )
        
        with gr.Tabs():
            # Crawl tab
            with gr.TabItem("数据抓取"):
                crawl_components = _create_crawl_tab_components()
                crawl_components["start_button"].click(
                    process_data,
                    inputs=_get_crawl_tab_inputs(crawl_components, current_lang),
                    outputs=crawl_components["result_output"],
                )
            
            # Post-processing tab
            with gr.TabItem("数据后处理"):
                postproc_components = create_postprocessing_tab_content(
                    locale=locales.get("zh", {})
                )
            
            # Tag translator tab
            with gr.TabItem("标签翻译"):
                tag_translator_components = create_tag_translator_tab_content(
                    locale=locales.get("zh", {})
                )
        
        # Language switch handler
        switch_language = _create_language_switch_handler(
            locales, postproc_components, tag_translator_components
        )
        
        language_selector.change(
            switch_language,
            inputs=[language_selector],
            outputs=_get_language_switch_outputs(
                current_lang, title, language_selector,
                crawl_components, postproc_components, tag_translator_components
            ),
        )
        
        demo.launch(
            server_name=host,
            server_port=port,
            debug=debug,
            share=share,
            inbrowser=True
        )


if __name__ == "__main__":
    launch_webui()
