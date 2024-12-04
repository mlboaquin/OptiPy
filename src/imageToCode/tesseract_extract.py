import pytesseract
from PIL import Image
import os

class CodeExtractor:
    def __init__(self):
        # Set Tesseract path explicitly
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            raise RuntimeError(
                "Tesseract not found at expected path. Please install Tesseract OCR from: "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )
        
        # Configure Tesseract for code recognition
        self.custom_config = r'--oem 3 --psm 6'
    
    def extract_code_from_image(self, image_path):
        """Extract code from an image using Tesseract OCR"""
        try:
            # Load and preprocess the image
            image = Image.open(image_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Increase contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Increase resolution while maintaining aspect ratio
            scale_factor = 2
            image = image.resize(
                (image.width * scale_factor, image.height * scale_factor),
                Image.Resampling.LANCZOS
            )
            
            # Configure Tesseract with improved whitespace handling
            self.custom_config = (
                '--oem 3 '           # Use neural network mode
                '--psm 6 '           # Assume uniform text block
                '-c preserve_interword_spaces=1 '  # Preserve spaces between words
                '-c preserve_whitespace=1 '        # Preserve all whitespace
                '-c tessedit_char_blacklist=¬ '    # Remove problematic characters
            )
            
            # Extract text with raw output to preserve spacing
            extracted_text = pytesseract.image_to_string(
                image,
                config=self.custom_config,
                lang='eng'
            )
            
            return self._clean_extracted_text(extracted_text)
            
        except Exception as e:
            print(f"Error during extraction: {str(e)}")
            return None
    
    def _clean_extracted_text(self, text):
        """Clean up the extracted text while preserving indentation"""
        if not text:
            return None
        
        # Split into lines while preserving empty lines
        lines = text.splitlines(True)  # Keep the line endings
        
        # Remove duplicate lines while preserving order and structure
        seen_content = set()
        cleaned_lines = []
        previous_was_empty = False
        
        for line in lines:
            original_line = line
            stripped_content = line.strip()
            
            # Handle empty lines
            if not stripped_content:
                if not previous_was_empty:  # Only add if previous line wasn't empty
                    cleaned_lines.append('\n')
                    previous_was_empty = True
                continue
            
            previous_was_empty = False
            
            # Count leading spaces for indentation
            leading_space_count = len(line) - len(line.lstrip())
            
            # Fix common OCR character mistakes
            replacements = {
                '|': 'I',
                '›': '>',
                '‹': '<',
                "'": "'",
                '"': '"',
                '"': '"',
                '—': '-',
                '–': '-',
                '…': '...',
                '\t': '    ',
                ' .': '.',
                ' ,': ',',
                '( ': '(',
                ' )': ')',
                '[ ': '[',
                ' ]': ']',
                'from _': 'from_',
                'spider opened': 'spider_opened',
                'process spider': 'process_spider',
                'is item': 'is_item',
                'for 1 in': 'for i in',
                'yield 1': 'yield i',
            }
            
            # Clean the content
            cleaned_content = stripped_content
            for old, new in replacements.items():
                cleaned_content = cleaned_content.replace(old, new)
            
            # Apply additional fixes
            if cleaned_content:
                cleaned_content = self._fix_naming_patterns(cleaned_content)
                cleaned_content = self._fix_import_statements(cleaned_content)
                cleaned_content = self._fix_programming_keywords(cleaned_content)
            
            # Handle Python-specific indentation
            if cleaned_content.startswith('class ') or cleaned_content.startswith('def '):
                # Add extra newline before class and function definitions
                if cleaned_lines and cleaned_lines[-1].strip():
                    cleaned_lines.append('\n')
                # Ensure proper indentation for class/method bodies
                if leading_space_count == 0:
                    leading_space_count = 4 if cleaned_content.startswith('def ') else 0
            
            # Reconstruct the line with proper indentation
            if cleaned_content not in seen_content:
                seen_content.add(cleaned_content)
                # Calculate proper indentation
                if leading_space_count > 0:
                    # Round to nearest multiple of 4 for Python
                    leading_space_count = ((leading_space_count + 2) // 4) * 4
                
                final_line = ' ' * leading_space_count + cleaned_content + '\n'
                cleaned_lines.append(final_line)
        
        # Add final newline if needed
        if cleaned_lines and not cleaned_lines[-1].endswith('\n'):
            cleaned_lines.append('\n')
        
        # Join lines and normalize multiple empty lines
        cleaned_text = ''.join(cleaned_lines)
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text
    
    def _fix_naming_patterns(self, content):
        """Fix common naming patterns in code"""
        # Fix underscore-related issues in names
        words = content.split()
        for i, word in enumerate(words):
            if ' ' in word and not any(char in word for char in '"\''):
                # Replace spaces with underscores in identifiers
                words[i] = word.replace(' ', '_')
            # Fix number/letter confusion in common cases
            if word == '1n':
                words[i] = 'in'
            elif word == '1f':
                words[i] = 'if'
        return ' '.join(words)
    
    def _fix_import_statements(self, content):
        """Fix import statement formatting"""
        if any(keyword in content.lower() for keyword in ['import', 'from']):
            words = content.split()
            try:
                if 'from' in words:
                    from_idx = words.index('from')
                    import_idx = words.index('import')
                    if from_idx < import_idx:
                        return f"from {' '.join(words[from_idx + 1:import_idx])} import {' '.join(words[import_idx + 1:])}"
                elif 'import' in words:
                    import_idx = words.index('import')
                    return f"import {' '.join(words[import_idx + 1:])}"
            except (ValueError, IndexError):
                pass
        return content
    
    def _fix_programming_keywords(self, content):
        """Fix common programming keywords and patterns"""
        # Common programming keywords that might be misrecognized
        keyword_fixes = {
            'def1ne': 'define',
            'pr1nt': 'print',
            'funct1on': 'function',
            'wh1le': 'while',
            'ret urn': 'return',
            'y1eld': 'yield',
            'ra1se': 'raise',
            'cont1nue': 'continue',
            'pass word': 'password',
            'class ': 'class ',  # Keep the space after class
        }
        
        for old, new in keyword_fixes.items():
            content = content.replace(old, new)
        
        # Fix common code patterns
        if content.strip().startswith('//'):  # Convert // comments to # for Python
            content = content.replace('//', '#', 1)
        
        return content