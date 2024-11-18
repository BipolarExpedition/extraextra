#!/bin/sh

# Updates metadata using variables in template_vars.env
# To be used for updating already defined metadata in an
#     existing project, when the values in the template_vars.env
#     file have changed
# Currently updates information for project version,
#     project description, and project keywords

# TODO: Add updating of additional metadata

# save to restore working directory later
ORIGPATH="$(pwd)"

# configure path information and working directory
SCRIPTPATH="$0"
cd "$(dirname ${SCRIPTPATH})/.." || exit 253
PROJECTDIR="$(pwd)"

# source template_vars.env as defined in SOURCEFILE
SOURCEFILE="${PROJECTDIR}/template_vars.env"
if [ -f "${SOURCEFILE}" ]; then
    # shellcheck disable=SC1090
    . "$SOURCEFILE"
else
    echo "Error: environment variables file not found: ${SOURCEFILE}"
    exit 253
fi

KW=$(echo "${TPL_PROJECTKEYWORDS}" | python -c 'import sys;import re;print( ",".join(["\"{}\"".format(re.sub("[^a-zA-Z01-9 ]","",e.strip())) for e in (sys.stdin.read()).split(",") if e.strip()]) )')

SED_CMD=$(which sed)

$SED_CMD -E "s/version\s*=\s*\"[0-9\.\-\_a-zA-Z]+\"/version = \"${TPL_PROJECTVERSION}\"/g" "${PROJECTDIR}/pyproject.toml"
$SED_CMD -E "s/description\s*=\s*\".*?\"/description = \"${TPL_PROJECTDESCRIPTION}\"/g" "${PROJECTDIR}/pyproject.toml"
$SED_CMD -E "s/^#?\s*keywords\s*=\s*\[.*\]/keywords = [\"${KW}\"]/g" "${PROJECTDIR}/pyproject.toml"

$SED_CMD -i "s/^__version__ = .*/__version__ = \"${TPL_PROJECTVERSION}\"/" "${PROJECTDIR}/src/${TPL_PROJECTPREFIX}${TPL_PROJECTNAME}/__init__.py"
$SED_CMD -i "s/^__author__ = .*/__author__ = \"${TPL_COMPANYNAME}(${TPL_AUTHORNAME})\"/" "${PROJECTDIR}/src/${TPL_PROJECTPREFIX}${TPL_PROJECTNAME}/__init__.py"
$SED_CMD -i "s/^__email__ = .*/__email__ = \"${TPL_AUTHOREMAIL}\"/" "${PROJECTDIR}/src/${TPL_PROJECTPREFIX}${TPL_PROJECTNAME}/__init__.py"
$SED_CMD -i "s/^__projectDescription__ = .*/__projectDescription__ = \"${TPL_PROJECTDESCRIPTION}\"/" "${PROJECTDIR}/src/${TPL_PROJECTPREFIX}${TPL_PROJECTNAME}/__init__.py"
$SED_CMD -i "s/^__description__ = .*/__description__ = \"${TPL_PROJECTDESCRIPTION}\"/" "${PROJECTDIR}/src/${TPL_PROJECTPREFIX}${TPL_PROJECTNAME}/__init__.py"

# release = '0.0.1'
$SED_CMD -i "s/^\s*release\s*=.*?/release = '${TPL_PROJECTVERSION}'/" "${PROJECTDIR}/docs/conf.py"

echo "${TPL_PROJECTVERSION}" > "${PROJECTDIR}/src/${TPL_PROJECTPREFIX}${TPL_PROJECTNAME}/version.txt"

cd "${ORIGPATH}" || exit 252
