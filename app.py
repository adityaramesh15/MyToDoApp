todo_list = []

while True:
    print("----------------------------")
    print("To Do List")
    num = 1
    for todo in todo_list:
        print(f"{num}: {todo}")
        num += 1
    
    
    print()
    print("Actions: ")
    print("A - Add to-do item")
    print("R - Remove to-do item")
    print("X - Exit")
    choice = input("Enter your choice (A, R, or X): ").upper()

    if choice == "A":
        todo = input("Enter the to-do item: ")
        todo_list.append(todo)
        continue
    elif choice == "R":
        num = int(input("Enter the number of the item to remove: "))
        if num > 0 and num <= len(todo_list):
            todo_list.pop(num - 1)
        else: 
            print("Invalid Number")
        continue

    if choice == "X":
        break

    print("\nInvalid Choice")