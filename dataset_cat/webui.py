import logging
import os
import json
from pathlib import Path

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


# 作者信息提取函数
def extract_author_info(item):
    """
    Extract author information from different data sources.

    Args:
        item: ImageItem from waifuc containing metadata
    Returns:
        str: Author name or "Unknown" if not found
    """
    meta = item.meta
    logger.info(f"Extracting author info, meta keys: {list(meta.keys())}")
    # Danbooru
    if 'danbooru' in meta:
        danbooru_data = meta['danbooru']
        if 'tag_string_artist' in danbooru_data and danbooru_data['tag_string_artist']:
            artists = danbooru_data['tag_string_artist'].strip()
            if artists:
                return artists.replace(' ', ', ')
        if 'tags' in danbooru_data and isinstance(danbooru_data['tags'], dict):
            artists = danbooru_data['tags'].get('artist', [])
            if artists and isinstance(artists, list):
                return ', '.join(artists)
    # Safebooru
    if 'safebooru' in meta:
        safebooru_data = meta['safebooru']
        if 'tag_string_artist' in safebooru_data and safebooru_data['tag_string_artist']:
            artists = safebooru_data['tag_string_artist'].strip()
            if artists:
                return artists.replace(' ', ', ')
    # Zerochan
    if 'zerochan' in meta:
        zerochan_data = meta['zerochan']
        if 'author' in zerochan_data and zerochan_data['author']:
            return str(zerochan_data['author'])
        if 'uploader' in zerochan_data and zerochan_data['uploader']:
            return str(zerochan_data['uploader'])
        if 'tags' in zerochan_data and isinstance(zerochan_data['tags'], list):
            # 只保留最简单的作者推断逻辑
            for tag in reversed(zerochan_data['tags']):
                if tag.isalpha() and tag.islower() and 2 <= len(tag) <= 20:
                    return tag
    # Pixiv
    if 'pixiv' in meta:
        pixiv_data = meta['pixiv']
        if 'user' in pixiv_data and isinstance(pixiv_data['user'], dict):
            user_data = pixiv_data['user']
            if 'name' in user_data:
                return str(user_data['name'])
            if 'account' in user_data:
                return str(user_data['account'])
    # Gelbooru
    if 'gelbooru' in meta:
        gelbooru_data = meta['gelbooru']
        if 'tags' in gelbooru_data:
            import re
            artist_match = re.search(r'artist:(\w+)', str(gelbooru_data['tags']))
            if artist_match:
                return artist_match.group(1)
    # 通用tags
    if 'tags' in meta and isinstance(meta['tags'], dict):
        for tag in meta['tags']:
            if 'artist:' in tag:
                return tag.replace('artist:', '')
            if any(k in tag.lower() for k in ['creator', 'author', 'artist']):
                return tag
    # 兜底
    for source_key, source_data in meta.items():
        if isinstance(source_data, dict) and 'author' in source_data:
            author = source_data['author']
            if author and str(author).strip():
                return str(author).strip()
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


# WebUI 启动函数
def launch_webui():
    """Launch the Dataset Cat WebUI application."""
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
                    inputs=[
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
                    ],
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
            outputs=[
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
            ] + list(postproc_components.values()) + list(tag_translator_components.values()),
        )
        
        demo.launch(inbrowser=True)


if __name__ == "__main__":
    launch_webui()
