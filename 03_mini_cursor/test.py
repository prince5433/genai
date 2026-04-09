"""Simple program to add two numbers with basic input handling."""

try:
	first_number = float(input("Enter first number: "))
	second_number = float(input("Enter second number: "))

	total = first_number + second_number
	print(f"Sum: {total}")
except ValueError:
	print("Please enter valid numeric values.")
