"""Custom processing actions for image datasets.

This module contains custom actions that extend the waifuc action system,
providing additional functionality for image processing.
"""

import io
import os
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from waifuc.action import FilterAction, ProcessAction
from waifuc.model import ImageItem


class CropToDivisibleAction(ProcessAction):
    """Custom action that crops images to dimensions divisible by a specified factor."""

    def __init__(self, factor: int = 64) -> None:
        """Initialize the crop action.

        Args:
            factor: The factor by which image dimensions should be divisible.
        """
        self.factor = factor

    def process(self, item: ImageItem) -> ImageItem:
        """Process a single image item by cropping to divisible dimensions.

        Args:
            item: The image item to process.

        Returns:
            Processed image item with dimensions divisible by factor.
        """
        # Get image data
        image = item.image

        # Calculate new dimensions
        width, height = image.size
        new_width = (width // self.factor) * self.factor
        new_height = (height // self.factor) * self.factor

        # Return original if no change needed
        if new_width == width and new_height == height:
            return item

        # Calculate crop position (center crop)
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height

        # Crop image
        cropped_image = image.crop((left, top, right, bottom))

        # Return new ImageItem
        return ImageItem(cropped_image, item.meta)


class FileSizeFilterAction(FilterAction):
    """Custom filter action that filters images based on file size."""

    def __init__(self, max_size_mb: float = 10.0, min_size_mb: float = 0.1) -> None:
        """Initialize the file size filter.

        Args:
            max_size_mb: Maximum file size in megabytes.
            min_size_mb: Minimum file size in megabytes.
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.min_size_bytes = min_size_mb * 1024 * 1024

    def check(self, item: ImageItem) -> bool:
        """Check if image meets file size requirements.

        Args:
            item: The image item to check.

        Returns:
            True if file size is within specified range, False otherwise.
        """
        try:
            # Save image to memory buffer to estimate file size
            buffer = io.BytesIO()
            # Use original image format, default to PNG if unknown
            image_format = getattr(item.image, "format", "PNG") or "PNG"
            item.image.save(buffer, format=image_format)
            file_size = buffer.tell()
            buffer.close()

            # Check if file size is within range
            return self.min_size_bytes <= file_size <= self.max_size_bytes
        except Exception:
            # If unable to estimate file size, default to pass
            return True


class ImageCompressionAction(ProcessAction):
    """Custom action for intelligent image compression to target file size."""

    def __init__(
        self,
        target_size_mb: float = 10.0,
        quality_range: Tuple[int, int] = (20, 95),
        convert_to_jpeg: bool = True,
    ) -> None:
        """Initialize the image compression action.

        Args:
            target_size_mb: Target file size in megabytes.
            quality_range: JPEG quality range (min_quality, max_quality).
            convert_to_jpeg: Whether to convert non-JPEG formats to JPEG.
        """
        self.target_size_bytes = target_size_mb * 1024 * 1024
        self.min_quality, self.max_quality = quality_range
        self.convert_to_jpeg = convert_to_jpeg

    def _estimate_file_size(self, image: Image.Image, format_type: str = "JPEG", quality: int = 85) -> int:
        """Estimate file size after saving.

        Args:
            image: PIL Image object to estimate size for.
            format_type: Image format to save as.
            quality: JPEG quality for estimation.

        Returns:
            Estimated file size in bytes.
        """
        buffer = io.BytesIO()
        save_kwargs: Dict[str, Any] = {}

        if format_type.upper() == "JPEG":
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
            # Ensure image is RGB mode, JPEG doesn't support transparency
            if image.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                if "transparency" in image.info:
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")
        elif format_type.upper() == "PNG":
            save_kwargs["optimize"] = True

        try:
            image.save(buffer, format=format_type, **save_kwargs)
            size = buffer.tell()
            buffer.close()
            return size
        except Exception:
            buffer.close()
            return float("inf")  # Return infinity if save fails

    def _compress_jpeg(self, image: Image.Image) -> Tuple[Image.Image, int, int]:
        """Use binary search to find appropriate JPEG quality.

        Args:
            image: PIL Image object to compress.

        Returns:
            Tuple of (compressed_image, final_quality, file_size).
        """
        low_quality = self.min_quality
        high_quality = self.max_quality
        best_quality = high_quality
        best_image = image
        best_size = float("inf")

        # Ensure image is RGB mode
        if image.mode != "RGB":
            if image.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                if "transparency" in image.info:
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            else:
                image = image.convert("RGB")

        # Binary search for optimal quality
        while low_quality <= high_quality:
            mid_quality = (low_quality + high_quality) // 2
            estimated_size = self._estimate_file_size(image, "JPEG", mid_quality)

            if estimated_size <= self.target_size_bytes:
                # File size is acceptable, try higher quality
                best_quality = mid_quality
                best_image = image.copy()
                best_size = estimated_size
                low_quality = mid_quality + 1
            else:
                # File too large, reduce quality
                high_quality = mid_quality - 1

        return best_image, best_quality, best_size

    def process(self, item: ImageItem) -> ImageItem:
        """Process a single image item with compression.

        Args:
            item: The image item to process.

        Returns:
            Processed image item with compression applied.
        """
        image = item.image.copy()
        original_format = getattr(image, "format", "PNG") or "PNG"

        # Check current file size first
        current_size = self._estimate_file_size(image, original_format)

        # Return original if already smaller than target
        if current_size <= self.target_size_bytes:
            return item

        # Try JPEG compression
        if self.convert_to_jpeg or original_format.upper() == "JPEG":
            compressed_image, final_quality, final_size = self._compress_jpeg(image)

            # Update metadata
            new_meta = item.meta.copy()

            # Update filename extension to .jpg
            if "filename" in new_meta:
                filename = new_meta["filename"]
                name, _ = os.path.splitext(filename)
                new_meta["filename"] = f"{name}.jpg"

            # Add save parameters
            if "save_cfg" not in new_meta:
                new_meta["save_cfg"] = {}
            new_meta["save_cfg"]["format"] = "JPEG"
            new_meta["save_cfg"]["quality"] = final_quality
            new_meta["save_cfg"]["optimize"] = True

            return ImageItem(compressed_image, new_meta)

        # If not converting to JPEG, try PNG optimization (limited compression options)
        else:
            # PNG compression options are limited, mainly optimize
            optimized_size = self._estimate_file_size(image, "PNG")
            if optimized_size <= self.target_size_bytes:
                new_meta = item.meta.copy()
                if "save_cfg" not in new_meta:
                    new_meta["save_cfg"] = {}
                new_meta["save_cfg"]["format"] = "PNG"
                new_meta["save_cfg"]["optimize"] = True
                return ImageItem(image, new_meta)
            else:
                # PNG cannot reach target size, recommend converting to JPEG
                return item  # Return original image


# Export all action classes
__all__ = ["CropToDivisibleAction", "FileSizeFilterAction", "ImageCompressionAction"]
