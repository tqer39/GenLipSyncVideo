import scripts.create_and_copy_data as create_and_copy_data
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_custom_model.py <arg> --model-name <model_name>")
        sys.exit(1)
    arg = sys.argv[1]
    model_name = sys.argv[2]
    create_and_copy_data.main(["--model-name", model_name])
