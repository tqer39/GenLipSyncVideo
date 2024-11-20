import scripts.create_and_copy_data as create_and_copy_data
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_custom_model.py <arg>")
        sys.exit(1)
    arg = sys.argv[1]
    create_and_copy_data.main()
