import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

food_file = "D:\\Users\\jrls2_000\\Documents\\UNI\\_BA\\Data\\food.txt"
test_file = "D:\\Users\\jrls2_000\\Documents\\UNI\\_BA\\Data\\rsta20210244_si_002.txt"
target_file = os.path.join("G:\\Github\\BA-Jan\\test_results", "test_reactions.crs")

def main():
    foods = []
    with open(food_file, "r") as f_f:
        foods = f_f.readlines()
        for j, food in enumerate(foods):
            foods[j] = food.strip()
    
    with open(test_file, 'r') as f:
        lines = f.readlines()
        foodline = 0
        for i, line in enumerate(lines):
            if line.startswith("**"): lines[i] = "# " + line; continue
            if line == "\n": lines[i] = "# " + line ; continue
            if line.startswith('Reaction_ID'): lines[i] = "# " + line; foodline = i+1; continue
            splitline = line.split("\t")
            cat = "[" + splitline[2].strip() + "]"
            splitline = splitline[:2]
            splitline.append(cat)
            lines[i] = "\t".join(splitline) + "\n"

        lines.insert(foodline, "Food: " + ",".join(foods))
        with open(target_file, 'w') as target_f:
            target_f.writelines(lines)

if __name__ == '__main__':
    main()