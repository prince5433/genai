def count_digits(number):
    return len(str(abs(number)))

# Example usage:
if __name__ == '__main__':
    num = 12345
    print(f'Number of digits in {num} is: {count_digits(num)}')