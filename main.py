# Importing the necessary modules
import pandas as pd
import json

files = ["data/Timetable Workbook - SUTT Task 1 - S1.csv",
          "data/Timetable Workbook - SUTT Task 1 - S2.csv",
            "data/Timetable Workbook - SUTT Task 1 - S3.csv",
              "data/Timetable Workbook - SUTT Task 1 - S4.csv",
                "data/Timetable Workbook - SUTT Task 1 - S5.csv",
                 "data/Timetable Workbook - SUTT Task 1 - S6.csv"]     # path to files
parsed = []
for filenumber in range(len(files)):
    file = files[filenumber]
    df = pd.read_csv(file, index_col='COM COD', skiprows=1)     # Read the csv and store data in a dataframe object

    # Get course details
    first_row = df[~df['COURSE NO.'].isna()].values[0]
    course_no = first_row[0]
    course_title = first_row[1]
    credits = first_row[2:5]

    for credit in range(3):
        if credits[credit] == '-':
            credits[credit] = '0'
    [l, p, u] = credits
    credits = {"lecture": int(l), "practical": int(p), "units": int(u)}

    course_details = {"course_code": course_no, "course_title": course_title, "credits": credits}

    # Parse sections
    codes = {"L":"lecture", "P":"practical", "T":"tutorial"}
    sections = []
    teachers = df[~df['INSTRUCTOR-IN-CHARGE / Instructor'].isna()].values       # Extracting all rows containing an instructor name
    for instructor in teachers:
        if type(instructor[5]) is not float:        # Create new section whenever sec exists
            number = instructor[5]
            course_type = codes[number[0]]
            instructors = [instructor[6]]
            room = str(int(instructor[7]))
            times = instructor[8].split()

            # Dealing with various days and time slots
            days = []
            slots = []
            day = []
            slot = []
            for time in times:
                if time.isalpha():
                    day.append(time)
                    if slot != []:
                        slots.append(slot)
                        slot = []
                else:
                    if day != []:
                        days.append(day)
                        day = []
                    slot += [int(time)+7, int(time)+8]
        
            slots.append(sorted(list(set(slot))))       # Appending only distinct slots after sorting. Ex: [13,14,14,15] -> [13,14,15]
            timing = []
            for unique in range(len(days)):
                for day in days[unique]:
                    timing.append({"day": day, "slots": slots[unique]})
            section = {"section_type": course_type, "section_number": number, "instructors":instructors, "room": room, "timing": timing}
            sections.append(section)

        else:       # append instructor to most recent section
            sections[-1]['instructors'].append(instructor[6])

    course_details["sections"] = sections
    parsed.append(course_details)

    print("Progress:", filenumber+1, "/", len(files), "("+str((filenumber+1)*100//len(files))+"%)")

with open('parsed.json', 'w') as json_file:
    json.dump(parsed, json_file)

print("Generated JSON File: parsed.json")