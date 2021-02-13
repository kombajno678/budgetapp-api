from difflib import SequenceMatcher

def similar(a, b):
    x = SequenceMatcher()
    x.set_seqs(a, b)
    return x.ratio()

print(f"similarity = {similar('ala ma kota', 'ala ma kota'):.2}")
print(f"similarity = {similar('ala ma kota', 'ala ma psa'):.2}")
print(f"similarity = {similar('ala ma kota', 'kota ma ala'):.2}")
print(f"similarity = {similar('ala ma kota', '0123456789'):.2}")

