import tiktoken

encoder=tiktoken.encoding_for_model('gpt-4o')

print("Vocab size:", encoder.n_vocab)#20019(200k)
#vocab size basically means kitne unique tokens hai model ke paas, jitne zyada tokens honge utna hi model zyada complex aur nuanced language ko samajh payega.

text="The cat sat on the mat"
tokens=encoder.encode(text)
print("Tokens:", tokens) #Tokens: [976, 9059, 10139, 402, 290, 2450]

my_tokens=[976, 9059, 10139, 402, 290, 2450]
decoded_text=encoder.decode(my_tokens)
print("Decoded Text:", decoded_text) #Decoded Text: The cat sat on the mat