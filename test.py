text = "aboba aboba привет оплатить игрь как утебя деа меня зовут сергей и я хочу получить от вас оплату"
trigger = "оплат"
action = ""

splited_text = text.split(' ')
for i, word in enumerate(splited_text):
    if trigger in word:
        splited_text[i] = action
text = ' '.join(list(filter(('').__ne__, splited_text)))

print(text)