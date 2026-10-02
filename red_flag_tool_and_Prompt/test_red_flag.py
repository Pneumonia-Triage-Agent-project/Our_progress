from tools.red_flag_tool import check_red_flags

tests = [
    "my child has a fever for two days and a cough",
    "He is having trouble breathing and his lips are turning blue",
    "He is struggling to breathe"
]

for text in tests:
    print(text)
    print(check_red_flags.invoke({"symptoms":text}))
    print()