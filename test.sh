RED='\033[0;31m'
GREEN='\033[0;32m'
RESET='\033[0m'

for i in {1..10}
do
    file="instance$(printf "%02d" "$i")"
    python bimaru/bimaru.py < tests/"$file".txt > tests/"$file".myout
    diff tests/"$file".out tests/"$file".myout && \
      echo -e "${GREEN}TEST PASS: $file${RESET}" || \
      echo -e "${RED}TEST FAIL: $file${RESET}"
done
