import sys
if (len(sys.argv) < 2):
    print("Укажите путь к файлу") 
    sys.exit(1)
try:
    with open(sys.argv[1], "r", encoding="utf-8") as file:
        text = file.read()
except FileNotFoundError:
    print("Файл не найден.")
    sys.exit(1)
if not text.strip():
    print("Файл пустой.")
    sys.exit(1)

clean_text = ""

for i in text:
    if i.isalpha():
        clean_text += i
    else:
        clean_text += " "

words = clean_text.lower().split()
if not words:
    print("Нету слов")
    sys.exit(1)

unique = set(words)
maxlength = 0
counts = {word: words.count(word) for word in unique}
for word in unique:
    if maxlength < len(word):
        maxlength = len(word)
        
def get_count(pair: tuple[str, int]) -> int:
    return pair[1]
sorted_words = sorted(counts.items(), key=get_count, reverse=True)
top10 = sorted_words[:10] 
print("Топ слов: ")
for a in top10:
     print(a[0] + ": " + str(a[1]))
print("Уникальных слов: " + str(len(unique)))
print("Длина самого длинного слова: " + str(maxlength))
