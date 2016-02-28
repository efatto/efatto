#!/bin/bash
shopt -s nullglob
FILES=/opt/simplerp/buildout/parts/simplerp/translation_simplerp/i18n/*.po
ARGS=$@

for db in $ARGS
do
    echo "Elaborazione db $db ..."
    for f in $FILES
    do
        echo "Elaborazione file $f ..."
        /opt/simplerp/buildout/bin/start_odoo --language=it_IT --i18n-import=$f --i18n-overwrite  -d $db
    done
done