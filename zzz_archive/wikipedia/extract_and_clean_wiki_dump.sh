#!/bin/sh
set -e

WIKI_DUMP_FILE_IN="enwiki-latest-pages-articles.xml.bz2"
WIKI_DUMP_FILE_OUT=${WIKI_DUMP_FILE_IN%%.*}.txt
DIRECTORY='/Users/alialvarez/Desktop/STUDIES/github/code_library/wikipedia/wikiextractor'

# clone the WikiExtractor repository
if [ ! -d "$DIRECTORY" ]; then
  # Control will enter here if $DIRECTORY doesn't exist.
  git clone https://github.com/attardi/wikiextractor.git
fi



# extract and clean the chosen Wikipedia dump
echo "Extracting and cleaning $WIKI_DUMP_FILE_IN to $WIKI_DUMP_FILE_OUT..."
python3 -m wikiextractor.WikiExtractor  $WIKI_DUMP_FILE_IN --processes 8 -q -o - \
| sed "/^\s*\$/d" \
| grep -v "^<doc id=" \
| grep -v "</doc>\$" \
> $WIKI_DUMP_FILE_OUT
echo "Succesfully extracted and cleaned $WIKI_DUMP_FILE_IN to $WIKI_DUMP_FILE_OUT"