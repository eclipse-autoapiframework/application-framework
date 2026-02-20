#!/bin/bash
set -e

# Check required tools
for cmd in conan jq; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: Required tool '$cmd' is not installed."
        exit 1
    fi
done

usage() {
    echo "Usage: $0"
    echo -e "\t--get-package PKG_NAME VERSION ARCH BUILD_TYPE COMPILER_VERSION CPP_STD"
    echo -e "\t--get-path PKG_NAME VERSION"
    exit 1
}

get_path() {
    local pkg_name="$1"
    local version="$2"

    json_data=$(conan list "${pkg_name}/${version}#*:*" --format json)
    if [ -z "$json_data" ] || [ "$json_data" == "null" ]; then
        echo "Error: No data found for ${pkg_name}/${version} in local cache."
        exit 1
    fi

    revision=$(echo "$json_data" | jq -r ".\"Local Cache\".\"${pkg_name}/${version}\".revisions | keys[0]")
    package=$(echo "$json_data" | jq -r ".\"Local Cache\".\"${pkg_name}/${version}\".revisions.\"${revision}\".packages | keys[0]")

    conan cache path "${pkg_name}/${version}#${revision}:${package}"
}

# Main argument parsing
if [ $# -lt 3 ]; then
    usage
fi

func="$1"
pkg_name="$2"
version="$3"
shift 3

case "$func" in
    --get-path)
        if [ $# -ne 0 ]; then usage; fi
        get_path "$pkg_name" "$version"
        ;;
    --get-package)
        if [ $# -ne 4 ]; then usage; fi
        get_package "$pkg_name" "$version" "$@"
        ;;
    *)
        usage
        ;;
esac
