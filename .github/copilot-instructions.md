We are building a Python package for end-to-end dataset creation, including data fetching, processing, and publishing. The package is primarily designed for anime-related datasets.

## Core Libraries and Tools

1. **Data Fetching**: We use libraries like `waifuc` and `gallery-dl` for fetching data from various sources. When providing examples or instructions related to data fetching, always prioritize these libraries.

2. **Data Processing**: For image processing, we are likely to use libraries such as `Pillow` or `OpenCV`. When suggesting image processing solutions, ensure compatibility with these libraries.

3. **Dataset Publishing**: For publishing datasets, we use tools like `huggingface-hub`. When providing examples for dataset publishing, include instructions for integrating with Hugging Face.

## Code Style Standards

4. **Type Annotations**: Always include type annotations for all function parameters, return values, and complex variables. Use `from typing import` for type hints.

5. **Comments and Documentation**: 
   - All comments and docstrings must be written in English
   - Use Google-style docstrings with proper Args, Returns, and Raises sections
   - Include meaningful inline comments explaining the "why", not the "what"

6. **Code Formatting**:
   - Use double quotes `"` for strings (single quotes only to avoid escaping)
   - Maximum line length: 120 characters
   - Use 4 spaces for indentation
   - Follow Black formatting standards

7. **Import Organization**:
   - Group imports in order: standard library, third-party, local imports
   - Sort imports alphabetically within each group
   - Separate groups with blank lines

8. **Naming Conventions**:
   - Variables and functions: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Use descriptive names, avoid abbreviations

9. **Focus on Usability**: Provide examples and instructions that are beginner-friendly and easy to integrate into our workflow.
