# test_image_to_code.py
from imageToCode import CodeExtractor
from PIL import Image
import io

def test_code_extraction(image_path):
    # Open the image
    image = Image.open(image_path)
    
    # Tilt the image by 2 degrees
    tilted_image = image.rotate(2, expand=True)
    
    # Convert the tilted image to a byte stream
    byte_stream = io.BytesIO()
    tilted_image.save(byte_stream, format='PNG')
    byte_stream.seek(0)
    
    # Create an instance of CodeExtractor
    extractor = CodeExtractor()
    
    # Extract code from the byte stream
    extracted_code = extractor.extract_code_from_image(byte_stream)
    
    # Print the extracted code
    if extracted_code:
        print("Extracted Code:")
        print(extracted_code)
    else:
        print("No code extracted or an error occurred.")

if __name__ == "__main__":
    # Path to the image containing code
    image_path = "src/dataset/test/images/image_7.png"
    
    # Run the test
    test_code_extraction(image_path)