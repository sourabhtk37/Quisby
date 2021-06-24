#! /usr/bin/bash

dev_flag='false'

echo "Checking for python"
if ! command -v python &>/dev/null; then
    echo "python required. Exiting"
    exit
fi

usage () {
  echo -e "\nInstall and configures necessary packages and software required for quisby"
  echo -e "\n Usage: $0 [-aws] [-azure] [-dev]"
  echo -e "optional args:"
  echo -e "\t -aws: setup aws"
  echo -e "\t -azure: setup azure"
  echo -e "\t -dev: setup development env"
}

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

# Check for google sheet creds
setup_gcp_credentials() {
  
  if ! command -v gcloud &>/dev/null; then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-345.0.0-linux-x86_64.tar.gz
    tar -xf google-cloud-sdk-345.0.0-linux-x86_64.tar.gz
    ./google-cloud-sdk/install.sh
    rm -rf google-cloud-sdk-345.0.0-linux-x86_64.tar.gz google-cloud-sdk/
  else
    if [ ! -f ~/.config/gcloud/application_default_credentials.json ]; then
      gcloud init
      if gcloud auth application-default login; then
        echo "credentials configured"
      else
        echo "Google sheet credentials file not found!"
        echo "Visit the URL: https://console.cloud.google.com/apis/credentials"
        echo "Click on 'Create credentials' -> 'OAuth client ID' -> Provide name and select 'Desktop app' as application type"
        echo "Download the 'credentials.json' from credentials page to the working directory"
      fi
    fi
  fi
}

# Install dependencies
setup_development_env() {
  setup_gcp_credentials

  if ! command -v pip &>/dev/null; then
      echo "Pip not found. Try installing pip"
      exit
  else
    if ! command -v poetry &>/dev/null; then
      curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
      
    fi
  fi
  if poetry install; then
    echo "Dependencies installed via poetry"
  else
    pip install -r requirements.txt
  fi
  echo -e "\n\nQuisby successfully configure. You can now invoke 'poetry quisby [OPTIONS] <test location file>'"
}

install_quisby_package() {
  setup_gcp_credentials
  pip install quisby

  echo -e "\n\nQuisby successfully configure. You can now invoke 'quisby [OPTIONS] <test location file>'"
}

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
    -dev)
        dev_flag='true'
        setup_development_env
        shift
        ;;
    -h)
        usage
        shift
        ;;
    *)
        shift
        ;;
    esac
done

if [ "$dev_flag" == "false" ]; then
  install_quisby_package
fi