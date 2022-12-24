import json

if __name__ == "__main__":
    with open("data/2016_data.json", "r") as f:
        dirty_data = json.load(f)
    print(f"Number of dirty climbs: {len(dirty_data)}")
    clean_data = []
    grade_count = {}
    hold_count_per_grade = {}

    for climb in dirty_data:
        if "raw_text" in climb:
            continue

        grade = climb["grade"]

        # clean up grade_count that are read poorly
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
            if grade not in grade_count:
                grade_count[grade] = 1
            else:
                grade_count[grade] +=1

            num_holds = len(climb["start_holds"] + climb["finish_holds"] + climb["middle_holds"])
            if grade not in hold_count_per_grade:
                hold_count_per_grade[grade] = [num_holds]
            else:
                hold_count_per_grade[grade].append(num_holds)



    print("Grade distribution:")
    for grade in grade_count:
        print(f"{grade}:\n\tNumber: {grade_count[grade]}\n\tAverage number of holds: {sum(hold_count_per_grade[grade])/len(hold_count_per_grade[grade])}")

    print(f"Number of clean climbs: {len(clean_data)}")
    with open("data/2016_data_clean.json", "w") as f:
        json.dump(clean_data, f, indent = 4)