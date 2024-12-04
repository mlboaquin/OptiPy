from imageToCode.code_extractor import CodeExtractor
from model.train_model import load_data

def train_model():
    # Initialize extractor
    extractor = CodeExtractor()

    # Load training data using the existing function
    train_dir = "src/dataset/train"
    image_paths, code_snippets = load_data(train_dir)

    print(f"Loaded {len(image_paths)} images and {len(code_snippets)} code snippets")

    # Train with the improved parameters
    extractor.train(
        image_paths=image_paths,
        code_snippets=code_snippets,
        epochs=100,
        batch_size=16,
        validation_split=0.2
    )

    # Save the model
    extractor.save_model("model_improved.pth")

if __name__ == "__main__":
    train_model() 