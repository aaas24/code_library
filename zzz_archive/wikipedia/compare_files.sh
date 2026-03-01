file1="/Users/alialvarez/Desktop/STUDIES/github/code_library/wikipedia/enwiki-latest-pages-articles.xml"
file2="/Users/alialvarez/Desktop/enwiki-latest-pages-articles.xml"

if cmp -s "$file1" "$file2"; then
    printf 'The file "%s" is the same as "%s"\n' "$file1" "$file2"
else
    printf 'The file "%s" is different from "%s"\n' "$file1" "$file2"
fi