#!/bin/bash

API="http://dadosabertos.rio.rj.gov.br/apiTransporte/apresentacao/rest/index.cfm/obterTodasPosicoes"
FOLDER="/root/movemos"
NEWFOLDER="$FOLDER/backups/$(date +%Y%m%d)"

mkdir -p $NEWFOLDER

cd $FOLDER

wget -O resultado.json $API

mv resultado.json "$NEWFOLDER/$(date +%Y-%m-%d_%H:%M).json"
