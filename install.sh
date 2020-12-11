#! /usr/bin/bash

echo "Checking for python"
if ! command -v python &>/dev/null; then
    echo "python required. Exiting"
    exit
fi

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
    -aws)
        setup_aws
        shift
        ;;
    -azure)
        setup_azure
        shift
        ;;
    *)
        shift
        ;;

    esac
done

# Configure aws creds
setup_aws() {
    echo "Checking for aws-cli"
    if ! command -v aws &>/dev/null; then
        echo "aws-cli required. Installing"
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        echo "Cleanup"
        rm -rf awscliv2.zip aws/
    fi

    echo "Configuring aws"
    if [ ! -f ~/.aws/credentials ]; then
        echo "aws credentials file not found! Configuring"
        if aws configure; then
            echo "AWS credentials configured successfully"
        else
            echo "AWS configuration failed! Try again"
            if aws configure; then
                echo "Success"
            else
                echo "Failed. Exiting"
            fi
        fi
    fi

}

setup_azure() {
    # Configure azure login
    echo "Checking for azure-cli"
    if ! command -v az &>/dev/null; then
        echo "azure-cli not found. Installing"
        curl -L https://aka.ms/InstallAzureCli | bash
    fi

    echo "Logging in to azure via browser"
    if az login; then
        echo "Azure-cli configured"
    else
        echo "Configuring azure failed!"
    fi

}

# TODO: Add a check for virtual env
echo "Create virtual environment"
python -m venv venv
if python -m venv venv; then
    echo "Virtual environment configured"
else
    echo "python venv module not found. Exiting"
    exit
fi

echo "Activate virtual env"
source venv/bin/activate

# Install dependencies
if ! command -v pip &>/dev/null; then
    echo "Pip not found. Try installing pip"
else
    pip install -r requirements.txt
    echo "Installed dependencies"
fi

# Run setup.py to install the project
python setup.py install

echo -e "\n\nQuisby successfully configure. You can now invoke 'quisby <test location file>'"

# Check for google sheet creds
if [ ! -f credentials.json ]; then
    echo "Google sheet credentials file not found!"
    echo "Visit the URL and click on 'Enable the Google Sheet API' button: https://developers.google.com/sheets/api/quickstart/python"
    echo "Provide a Project name and save the 'credentials.json' file in the working directory of this project"
fi
