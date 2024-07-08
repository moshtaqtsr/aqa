#!/bin/bash

# Function to check if a Python library is installed
check_and_install() {
    package=$1
    import_name=$2
    if python3 -c "import $import_name" &> /dev/null; then
        echo "Library '$package' ($import_name) is already installed."
    else
        echo "Library '$package' ($import_name) is not installed. Installing now..."
        pip install $package
        if [ $? -eq 0 ]; then
            echo "Library '$package' installed successfully."
        else
            echo "Failed to install library '$package'. Please install it manually."
        fi
    fi
}

# Step 1: Download the latest version of aqa.py
wget -O ~/aqa.py https://raw.githubusercontent.com/moshtaqtsr/aqa/main/notebook/aqa.py

# Step 2: Add shebang line to the Python script
echo '#!/usr/bin/env python3' > ~/aqa
cat ~/aqa.py >> ~/aqa
rm ~/aqa.py

# Step 3: Make the script executable
chmod +x ~/aqa

# Step 4: Move the script to a directory in your PATH
sudo mv ~/aqa /usr/local/bin/

# Step 5: Check for required libraries and install if necessary
required_libraries=(
    "os:os"
    "argparse:argparse"
    "datetime:datetime"
    "biopython:Bio"
    "pandas:pandas"
    "jinja2:jinja2"
    "openpyxl:openpyxl"
)

for lib in "${required_libraries[@]}"; do
    package=${lib%%:*}
    import_name=${lib##*:}
    check_and_install $package $import_name
done

echo "Installation complete. You can now run 'aqa' from any directory."
echo "All required libraries are installed."
