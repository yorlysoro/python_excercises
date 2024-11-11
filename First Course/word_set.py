def text_split(initial, final, text):
    return text[initial:final]


print("Enter the initial index")
initial = int(input())
print("Enter the final index")
final = int(input())

print(text_split(initial, final, "Hello, world!"))
