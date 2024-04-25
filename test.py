import re

catalysts="[a, b, c * d,   (e f)]".strip()
catalysts = re.sub("\\|", ",", catalysts)
catalysts = re.sub("\\*", "&", catalysts)
catalysts = re.sub("\\s*\\(\\s*", "(", catalysts)
catalysts = re.sub("\\s*\\)\\s*", ")", catalysts)
catalysts = re.sub("\\s*&\\s*", "&", catalysts)
catalysts = re.sub("\\s*,\\s*", ",", catalysts)
catalysts = re.sub("\\s+", ",", catalysts)

print(catalysts)