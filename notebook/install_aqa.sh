#!/bin/bash

# Step 1: Download the latest version of aqa.py
wget -O ~/aqa.py https://github.com/moshtaqtsr/aqa/blob/main/notebook/aqa.py

# Step 2: Add shebang line to the Python script
echo '#!/usr/bin/env python3' > ~/aqa
cat ~/aqa.py >> ~/aqa
rm ~/aqa.py

# Step 3: Make the script executable
chmod +x ~/aqa

# Step 4: Move the script to a directory in your PATH
mv ~/aqa /usr/local/bin/

echo "Installation complete. You can now run 'aqa' from any directory."
