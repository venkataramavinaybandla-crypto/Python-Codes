
from nltk.corpus import wordnet as wn

print("xxxx WElCOME TO DICTIONARY xxxx ")

word = input("Enter a word: ").strip().lower()

synsets = wn.synsets(word)

if not synsets:
    print("/nNo Meanings Found")
    exit()
else:
    print(f"Meanings of '{word}' : \n")
    for i,s in enumerate(synsets, 1):
        print(f"{i}. Meaning:")
        print("  ", s.definition())

        examples = s.examples()
        if examples:
            print("Examples : ")
            for ex in examples:
                print("   - ", ex)
        print()
        print("___________________________________________________________________________")
