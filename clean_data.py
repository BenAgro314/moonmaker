import json

if __name__ == "__main__":
    with open("data/2016_data.json", "r") as f:
        dirty_data = json.load(f)
    print(f"Number of dirty climbs: {len(dirty_data)}")
    clean_data = []
    grades = {}

    for climb in dirty_data:
        if "raw_text" in climb:
            continue

        grade = climb["grade"]

        # clean up grades that are read poorly
        if grade in ["7At", "6Bt", "7Bt+", "6Bt+", "6B+t", "7At+", "6 B+", "6Ct+", "7A+t", "7Bt"]:
            grade_letters = list(grade)
            if " " in grade_letters:
                grade_letters.remove(" ")
            for i, l in enumerate(grade):
                if l == "t":
                    grade_letters[i] = ""
            grade = "".join(grade_letters)
            climb["grade"] = grade


        if grade in ["6B+", "6C", "6C+", "7A", "7A+", "7B", "7B+", "7C", "7C+", "8A", "8A+", "8B", "8B+"]:
            clean_data.append(climb)
            if grade not in grades:
                grades[grade] = 1
            else:
                grades[grade] +=1

    print("Grade distribution:")
    for grade in grades:
        print(f"{grade}: {grades[grade]}")
    
    print(f"Number of clean climbs: {len(clean_data)}")
    with open("data/2016_data_clean.json", "w") as f:
        json.dump(clean_data, f, indent = 4)