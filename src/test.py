from imageToCode import CodeExtractor
import os
import json

def test_single_image():
    # Test parameters
    test_image = "src/dataset/test/images/image_3.png"
    
    print(f"Testing image: {test_image}")
    print("-" * 80)
    
    try:
        # Initialize Tesseract extractor
        extractor = CodeExtractor()
        
        # Extract code from test image
        extracted_code = extractor.extract_code_from_image(test_image)
        
        if extracted_code:
            print("\nExtracted Code:")
            print("-" * 40)
            print(extracted_code)
            print("-" * 40)
            
            # Print diagnostic information
            print("\nDiagnostic Information:")
            print(f"1. Number of lines: {len(extracted_code.split(chr(10)))}")
            print(f"2. Characters extracted: {len(extracted_code)}")
            print("3. Special characters found:", 
                  [c for c in set(extracted_code) if not c.isalnum() and c not in [' ', '\n', '\t']])
        else:
            print("\nNo code was extracted from the image.")
        
    except Exception as e:
        print(f"\nError during extraction: {str(e)}")
        raise

if __name__ == "__main__":
    test_single_image()

