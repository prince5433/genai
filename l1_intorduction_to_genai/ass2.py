class ASCIITokenizer:
    
    def encode(self, text):
        # Har character ko uske ASCII number me convert karte hain
        # ord(c) → character ko integer (ASCII value) me convert karta hai
        tokens = [ord(c) for c in text]
        return tokens

    def decode(self, tokens):
        # Har ASCII number ko wapas character me convert karte hain
        # chr(t) → integer ko character me convert karta hai
        text = ''.join(chr(t) for t in tokens)
        return text


# Test
tokenizer = ASCIITokenizer()

# Encoding: text → numbers
encoded = tokenizer.encode("Hello World")
print(encoded)  
# Example output: [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100]

# Decoding: numbers → text
decoded = tokenizer.decode(encoded)
print(decoded)  
# Output: "Hello World"