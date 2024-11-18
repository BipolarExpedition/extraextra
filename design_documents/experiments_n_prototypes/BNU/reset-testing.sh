#!/bin/sh

# procedure to print a warning message in yellow
warning() {
    printf "\033[1;33m%s\033[0m\n" "$1"
}

# procedure to print an error message in red
error() {
    printf "\033[1;31m%s\033[0m\n" "$1"
}


# Source the global variables
. ./shared-defs.sh


TOVERSION=$(echo "$1" | tr '[:upper:]' '[:lower:]')

case "${TOVERSION}" in
    "1.3")
        doUPDATE3=1
        ;;
    "1.2")
        doUPDATE2=1
        ;;
    "1.1")
        doUPDATE1=1
        ;;
    "original")
        doORIGINAL=1
        ;;
    *)
        echo "ERROR: Unknown parameter ${TOVERSION}"
        exit 1
        ;;
esac

if [ "$doORIGINAL" -eq "1" ]; then
    echo "Removing testing directory ${gTESTING}"
    rm -rf "${gTESTING}"

    echo "Setting to original distribution"
    unzip "${gORIGINAL}" -d "${gTESTING}"
fi

if [ "$doUPDATE1" -eq "1" ]; then
    echo "Not implemented yet"
    exit 2
fi

if [ "$doUPDATE2" -eq "1" ]; then
    echo "Not implemented yet"
    exit 2
fi

if [ "$doUPDATE3" -eq "1" ]; then
    echo "Not implemented yet"
    exit 2
fi
