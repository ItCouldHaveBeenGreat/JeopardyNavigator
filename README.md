1. Raw data was copypasted out of https://j-archive.com/listseasons.php
1. Post processing was done with the following shell command
 * The goal of the post processing was to uniformly format the data, remove extraneous text, and remove any special rounds that break continuity
 * Yes, it's madness:
 ```
cat jepoardy_games_raw.txt | tr '\t' ',' | sed -e 's/aired//g' | grep -v -e 'Professors Tournament' -e 'Tournament of Champions' -e 'College Championship' -e 'Back to School Week' -e 'Teen Tournament' -e 'Celebrity Jeopardy' -e 'vs. Watson' -e 'All-Star Games'  -e 'Kids Week' | cut -d ',' -f 1-3 | sed -e 's/ vs\. /,/g' | tr -d '#' | sed -e 's/  / /g' | sed -e 's/ ,/,/g' | sed -e 's/, /,/g' | sed -e 's/,/, /g' | sed -e 's/ $//g' | sed '1! G;h;$!d' > jepoardy_games.csv
```
