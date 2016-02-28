#!/bin/bash
shopt -s nullglob
FILES=/home/sergio/buildout/parts/simplerp/translation_simplerp/i18n/*.po
DATABASE=inserire_il_nome_del_db

for f in $FILES
do
  echo "Elaborazione file $f ..."
  bin/start_odoo --language=it_IT --i18n-import=$f --i18n-overwrite  -d $DATABASE
done