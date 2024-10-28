# This program reads patient height and weight data from a CSV file, calculates their
# Body Mass Index (BMI), handles any formatting errors, and saves the results to a text file.
# 10-28-2024
# CSC121 M5Lab
# William Beckham

import csv

def calculate_bmi(weight, height):
    """
    Calculate the Body Mass Index (BMI) given weight and height.
    
    Parameters:
    weight (float): The weight of the patient in pounds.
    height (float): The height of the patient in inches.
    
    Returns:
    float: The calculated BMI value rounded to two decimal places.
    """
    return round(weight / (height ** 2) * 703, 2)

def get_weight_status(bmi):
    """
    Determine the weight status based on the BMI value.
    
    Parameters:
    bmi (float): The calculated BMI value.
    
    Returns:
    str: The weight status as one of "Underweight", "Normal", "Overweight", or "Obese".
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi >= 18.5 and bmi < 25:
        return "Normal"
    elif bmi >= 25 and bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def main():
    """
    Main function to read patient data from a CSV file, calculate 
    BMI for each patient, determine the weight status, and save the 
    results to two files: 'bmi.txt' for BMI and 'patient_bmi.csv'
    for detailed patient data.
    
    It handles errors related to non-numeric height and weight values
    and prints appropriate error messages for each patient.
    """
    input_file = 'patients.csv'
    bmi_text_file = 'bmi.txt'
    bmi_csv_file = 'patient_bmi.csv'
    
    with open(input_file, 'r') as infile, open(bmi_text_file, 'w') as outfile, open(bmi_csv_file, 'w', newline='') as csvfile:
        reader = csv.reader(infile)
        writer = csv.writer(csvfile)
        
        # Write the header for the CSV file
        writer.writerow(['Patient ID', 'Height', 'Weight', 'BMI', 'Weight Status'])
        
        # Skip the header in the input file
        next(reader)
        
        for row in reader:
            patient_id, height, weight = row
            height_error = False
            weight_error = False
            
            try:
                height = float(height)
            except ValueError:
                height_error = True
            
            try:
                weight = float(weight)
            except ValueError:
                weight_error = True
            
            if height_error and weight_error:
                print(f"Error: Non-numeric data for both height and weight for Patient ID: {patient_id}")
            elif height_error:
                print(f"Error: Non-numeric height for Patient ID: {patient_id}")
            elif weight_error:
                print(f"Error: Non-numeric weight for Patient ID: {patient_id}")
            else:
                bmi = calculate_bmi(weight, height)
                weight_status = get_weight_status(bmi)
                print(f"Patient ID: {patient_id}, BMI: {bmi:.2f}, Weight Status: {weight_status}")
                outfile.write(f"{patient_id}, {bmi:.2f}, {weight_status}\n")
                writer.writerow([patient_id, height, weight, bmi, weight_status])

    print("BMI calculation and weight status determination complete. Results saved to bmi.txt and patient_bmi.csv.")

if __name__ == "__main__":
    main()