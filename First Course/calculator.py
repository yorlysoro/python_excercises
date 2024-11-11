def calculator():
    print("Welcome to the calculator!")
    print("Please enter the first number")
    first_number = int(input())
    print("Please enter the second number")
    second_number = int(input())
    print("Please enter the operation you would like to perform")
    operation = input()
    if operation == "+":
        print(first_number + second_number)
    elif operation == "-":
        print(first_number - second_number)
    elif operation == "*":
        print(first_number * second_number)
    elif operation == "/":
        print(first_number / second_number)
    else:
        print("Invalid operation")


calculator()
