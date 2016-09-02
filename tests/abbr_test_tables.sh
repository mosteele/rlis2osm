#!/usr/bin/env bash

set -e
shopt -s expand_aliases

OSPN_EPSG=2913
PGDBNAME='rlis_abbr_test'
PGHOST='localhost'
PGCLIENTENCODING='UTF8'
DATASETS=( 'streets' 'trails' )
PROJECT_DIR="$( cd $(dirname ${0}); dirname $(pwd -P) )"

# cygwin-psql can't read file paths starting like '/cygdrive/...'
if [[ "${OSTYPE}" == 'cygwin' ]]; then
    PROJECT_DIR="$( cygpath -w ${PROJECT_DIR} )"
fi

DATA_DIR="${PROJECT_DIR}/data"

# process command line options
while getopts ':p:u:' opt; do
    case "${opt}" in
        p)
            PGPASSWORD="${OPTARG}"
            ;;
        u)
            PGUSER="${OPTARG}"
            ;;
    esac
done

# if user doesn't supply postgres username and password prompt them
if [[ -z "${PGUSER}" ]]; then
    read -p $'Enter postgres user name:\n' PGUSER
fi

if [[ -z "${PGPASSWORD}" ]]; then
    nl=$'\n'
    read -s -p "Enter postgres password for user '${PGUSER}':${nl}" PGPASSWORD
fi

export PGPASSWORD
alias psql="psql -U ${PGUSER} -h ${PGHOST}"


create_postgis_db() {
    # if the db exists do nothing
    # http://stackoverflow.com/questions/1454927

    if ! psql -lqtA | grep -q "^${PGDBNAME}|"; then
        createdb -U "${PGUSER}" -h "${PGHOST}" "${PGDBNAME}"
        psql -d "${PGDBNAME}" -c 'CREATE EXTENSION postgis;'
    fi
}

load_data() {
    for ds in "${DATASETS[@]}"; do
        ds_path="${DATA_DIR}/${ds}.shp"

        if [[ ! -f "${ds_path}" ]]; then
            zip_path="${ds_path%.*}.zip"

            if [[ -f "${zip_path}" ]]; then
                unzip -o "${zip_path}" -d "${DATA_DIR}"
            else
                echo "file: ${ds_path} doesn't not exist, script can't proceed"
                exit 1
            fi
        fi

        # postgres copy command (invoked by -D option) can't handle literal
        # newlines so sed replaces them with newline characters
        shp2pgsql -d -s "${OSPN_EPSG}" -I -D -W 'LATIN1' "${ds_path}" \
            | sed 's/\n/\\n/g' | psql -d "${PGDBNAME}"
    done
}

create_word_table() {
    abbr_sql="${PROJECT_DIR}/tests/word_table.sql"
    psql -d "${PGDBNAME}" -v ON_ERROR_STOP=1 -f "${abbr_sql}"
}

main() {
    create_postgis_db
    load_data
    create_word_table
}

main