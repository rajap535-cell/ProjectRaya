import os
import nbformat

# Path to your ProjectRaya folder
PROJECT_FOLDER = r"C:\Users\RD\OneDrive\Desktop\raya_cleaned\ProjectRaya"

# Walk through all files in the folder
for root, dirs, files in os.walk(PROJECT_FOLDER):
    for file in files:
        if file.endswith(".ipynb"):
            file_path = os.path.join(root, file)
            try:
                # Read the notebook
                nb = nbformat.read(file_path, as_version=4)

                # Remove broken widgets metadata if it exists
                if "widgets" in nb.metadata:
                    print(f"Fixing notebook: {file_path}")
                    del nb.metadata["widgets"]

                # Write back the fixed notebook
                nbformat.write(nb, file_path)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

print("All notebooks processed!")
