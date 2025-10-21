import pytesseract
from PIL import Image
import os

class CodeExtractor:
    def __init__(self):
        # Set Tesseract path explicitly
        tesseract_path = r'C:\Users\Mark\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
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
        """Clean up the extracted text specifically for Python code"""
        if not text:
            return None
        
        # Split into lines while preserving empty lines
        lines = text.splitlines(True)
        
        # Remove duplicate lines while preserving structure
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
            
            # Count leading spaces for Python indentation
            leading_space_count = len(line) - len(line.lstrip())
            
            # Fix common OCR mistakes in Python code
            replacements = {
                # Basic character fixes
                '|': 'I',
                '›': '>',
                '‹': '<',
                "'": "'",
                '"': '"',
                '"': '"',
                '—': '-',
                '–': '-',
                '…': '...',
                '\t': '    ',  # Convert tabs to spaces (PEP 8)
                
                # Python-specific fixes
                'def1ne': 'define',
                'pr1nt': 'print',
                'wh1le': 'while',
                'y1eld': 'yield',
                'ra1se': 'raise',
                'ret urn': 'return',
                'pass word': 'password',
                'True1': 'True',
                'False1': 'False',
                'None1': 'None',
                'class1': 'class',
                
                # Python spacing fixes
                ' .': '.',
                ' ,': ',',
                '( ': '(',
                ' )': ')',
                '[ ': '[',
                ' ]': ']',
                '{ ': '{',
                ' }': '}'
            }
            
            # Clean the content
            cleaned_content = stripped_content
            for old, new in replacements.items():
                cleaned_content = cleaned_content.replace(old, new)
            
            # Fix Python-specific patterns
            if cleaned_content:
                # Fix method/variable naming patterns (convert spaces to underscores)
                if '_' in cleaned_content or ' ' in cleaned_content:
                    words = cleaned_content.split()
                    for i, word in enumerate(words):
                        if ' ' in word and not any(char in word for char in '"\''):
                            words[i] = word.replace(' ', '_')
                    cleaned_content = ' '.join(words)
                
                # Fix Python import statements
                if 'import' in cleaned_content or 'from' in cleaned_content:
                    cleaned_content = self._fix_python_imports(cleaned_content)
                
                # Fix common Python number/letter confusions in specific contexts
                if 'for ' in cleaned_content or 'if ' in cleaned_content:
                    cleaned_content = cleaned_content.replace('1n ', 'in ')
                    cleaned_content = cleaned_content.replace('1f ', 'if ')
            
            # Handle Python indentation (should be multiples of 4 spaces)
            if leading_space_count > 0:
                leading_space_count = ((leading_space_count + 2) // 4) * 4
            
            # Add extra newline before class and function definitions
            if cleaned_content.startswith(('class ', 'def ')) and cleaned_lines and cleaned_lines[-1].strip():
                cleaned_lines.append('\n')
            
            # Add the cleaned line with proper Python indentation
            if cleaned_content not in seen_content:
                seen_content.add(cleaned_content)
                final_line = ' ' * leading_space_count + cleaned_content + '\n'
                cleaned_lines.append(final_line)
        
        # Join lines and normalize empty lines per Python conventions
        cleaned_text = ''.join(cleaned_lines)
        
        # Ensure two blank lines before top-level classes/functions (PEP 8)
        cleaned_text = cleaned_text.replace('\nclass ', '\n\n\nclass ')
        cleaned_text = cleaned_text.replace('\ndef ', '\n\n\ndef ')
        
        # Normalize multiple empty lines to maximum of two (PEP 8)
        while '\n\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n\n', '\n\n\n')
        
        return cleaned_text
    
    def _fix_python_imports(self, content):
        """Fix Python import statement formatting"""
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
