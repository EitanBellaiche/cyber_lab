#!/bin/bash

set -e  # Exit on error

jail=$(pwd)
OS=$(uname -s)

# Function to get Python library path
get_py_lib_path() {
    python3 -c "import $1; print($1.__path__[0])"
}

# Function to handle mounting
do_mount() {
    mount --bind "$1" "$2" || { echo "Mounting $1 failed"; exit -1; }
}

# Function to check if a package is installed
is_package_installed() {
    dpkg -l "$1" &> /dev/null
}

# Function to check and install Python libraries
ensure_python_libs_installed() {
    for lib in "$@"; do
        if python3 -c "import $lib" &> /dev/null; then
            echo "$lib is installed."
        else
            echo "$lib not installed. Installing..."
            pip install "$lib" || { echo "Failed to install $lib"; exit -1; }
        fi
    done
}


# Check for Linux OS
if [ "$OS" != "Linux" ]; then
    echo "Unsupported OS"
    exit -1
fi

# Set up directory structure
mkdir -p "$jail"/{usr,lib,lib64,bin,etc,run,zoobar/{flask,sqlalchemy,werkzeug,itsdangerous,web3,dateutil,dotenv,eth_account,solcx,db},authsvc,banksvc,auth_secure_keys,bank_secure_keys}
# Check if python3-pip is installed
if is_package_installed python3-pip; then
    echo "python3-pip is already installed."
else
    echo "Installing python3-pip..."
    apt update && apt install -y python3-pip

    if is_package_installed python3-pip; then
        echo "python3-pip installed successfully."
    else
        echo "Failed to install python3-pip. Please check for errors."
        exit -1
    fi
fi

# Ensure Flask, SQLAlchemy, and Web3 are installed
ensure_python_libs_installed flask sqlalchemy web3 python-dateutil python-dotenv eth_account py-solc-x
  
# Dynamically get Python library paths
sqlalchemyPath=$(get_py_lib_path sqlalchemy)
flaskPath=$(get_py_lib_path flask)
werkzeugPath=$(get_py_lib_path werkzeug)
itsdangerousPath=$(get_py_lib_path itsdangerous)
web3Path=$(get_py_lib_path web3)
dateutilPath=$(get_py_lib_path dateutil)
dotenvPath=$(get_py_lib_path dotenv)
eth_accountPath=$(get_py_lib_path eth_account)
solcxPath=$(get_py_lib_path solcx)
typing_extensionsPath=$(python3 -c "import typing_extensions; print(typing_extensions.__file__)")

# Mount directories
do_mount /usr "$jail/usr"
do_mount /lib "$jail/lib"
do_mount /lib64 "$jail/lib64"
do_mount /bin "$jail/bin"
do_mount /etc "$jail/etc"
do_mount /run "$jail/run"
do_mount "$sqlalchemyPath" "$jail/zoobar/sqlalchemy"
do_mount "$flaskPath" "$jail/zoobar/flask"
do_mount "$werkzeugPath" "$jail/zoobar/werkzeug"
do_mount "$itsdangerousPath" "$jail/zoobar/itsdangerous"
do_mount "$web3Path" "$jail/zoobar/web3"
do_mount "$dateutilPath" "$jail/zoobar/dateutil"
do_mount "$dotenvPath" "$jail/zoobar/dotenv"
do_mount "$eth_accountPath" "$jail/zoobar/eth_account"
do_mount "$solcxPath" "$jail/zoobar/solcx"
cp "$typing_extensionsPath" "$jail/zoobar"

echo "Mount complete"

# Set permissions and ownership
chmod 770 "$jail"/{authsvc,banksvc,zoobar/{db,auth-server.py,bank-server.py,index.cgi}}
chmod 750 "$jail"/{auth_secure_keys,bank_secure_keys}
chown 33333:11111 "$jail"/{authsvc,auth_secure_keys}
chown 44444:11111 "$jail"/{banksvc,bank_secure_keys}
chown 38382:11111 "$jail"/zoobar/index.cgi
chown "$USER":11111 "$jail"/zoobar/{db,auth-server.py,bank-server.py}

echo "Permission setup complete"

# Check if libjansson-dev is installed
if is_package_installed libjansson-dev; then
    echo "libjansson-dev is already installed."
else
    echo "Installing libjansson-dev..."
    apt update && apt install -y libjansson-dev

    if is_package_installed libjansson-dev; then
        echo "libjansson-dev installed successfully."
    else
        echo "Failed to install libjansson-dev. Please check for errors."
        exit -1
    fi
fi

# Chec & Add Ethereum PPA and install solc
if is_package_installed solc; then
    echo "solc is already installed."
else
    echo "Adding Ethereum PPA and installing solc..."
    add-apt-repository -y ppa:ethereum/ethereum && apt update && apt install -y solc

    if is_package_installed solc; then
        echo "solc installed successfully."
    else
        echo "Failed to install solc. Please check for errors."
        exit -1
    fi
fi

# pyton script that generate keys
python3 "$jail/zoobar/generate_keys.py"