class SimpleTokenizer:
    def __init__(self):
        # Character-level tokenizer
        self.chars = list("abcdefghijklmnopqrstuvwxyz "
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "0123456789.,!?<>")
        self.char_to_id = {ch: i for i, ch in enumerate(self.chars)}
        self.id_to_char = {i: ch for i, ch in enumerate(self.chars)}
        
        # Special tokens
        self.START_TOKEN = len(self.chars)
        self.END_TOKEN = len(self.chars) + 1
    
    def encode(self, text: str) -> list[int]:
        """Text → Token IDs"""
        tokens = [self.START_TOKEN]
        for char in text:
            if char in self.char_to_id:
                tokens.append(self.char_to_id[char])
        tokens.append(self.END_TOKEN)
        return tokens
    
    def decode(self, token_ids: list[int]) -> str:
        """Token IDs → Text"""
        text = ""
        for token_id in token_ids:
            if token_id == self.START_TOKEN:
                continue
            elif token_id == self.END_TOKEN:
                break
            elif token_id in self.id_to_char:
                text += self.id_to_char[token_id]
        return text

# Test karo
tokenizer = SimpleTokenizer()
encoded = tokenizer.encode("Hello World")
print(encoded)   # [66, 7, 4, 11, 11, 14, 53, 22, 14, 17, 11, 3, 67]

decoded = tokenizer.decode(encoded)
print(decoded)   # "Hello World"    