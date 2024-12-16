"""
DuplicateDeleter.py
@author Kedar Abhyankar, krabhyankar@gmail.com
@version 1.0.0
@date 12/15/2024
"""

import json
import sys
from datetime import datetime

'''
The remove_duplicates function takes a parameter of file_data - identically structured JSON
entries. It then parses through the fields and compares for uniqueness as per the following rules:

1) IDs must be unique
2) Emails must be unique
3) Identical dates result in the entry further in the file being chosen.
4) Newer data is preferred over older data (as indicated by the date)

It saves the elements seen in a dictionary, seen_elements, and the elements to remove
in a dictionary, removed_elements. For the elements that are removed, it also includes
a new `reason` field as to why the element was removed.

It returns both of these dictionaries, as the return value.
'''
def remove_duplicates(file_data):
    # The set to save the seen elements in
    seen_elements = []
    # The set to save the elements we are removing in
    removed_elements = []

    # Iterate through the file data.
    for entry in file_data:

        # Assume the data is unique to start.
        duplicate = None
        reason = None

        # For every element in seen, check to see if the id matches, or if the email matches.
        # If it does, then mark it as such, set it as seen (by saving it to
        # the duplicate variable) and then marking the reason (by setting the `reason` variable).
        for existing_lead in seen_elements:
            if existing_lead['_id'] == entry['_id']:
                duplicate = existing_lead
                reason = "Duplicate id"
                break
            elif existing_lead['email'] == entry['email']:
                duplicate = existing_lead
                reason = "Duplicate email"
                break

        # If duplicate found, compare dates to keep the latest
        if duplicate:
            # Parse the dates since these are ISO formatted dates.
            existing_date = datetime.fromisoformat(duplicate['entryDate'])
            new_date = datetime.fromisoformat(entry['entryDate'])

            # Compare the dates and keep the newer one.
            if new_date > existing_date:
                # Save the removed element to removed_elements and include the reason, also
                # indicating if it was an older entry or not.
                removed_elements.append({
                    **duplicate,  # Include all fields from the duplicate
                    "reason": reason + " (older entry)"
                })
                seen_elements.remove(duplicate)
                seen_elements.append(entry)
            else:
                # Should the date not be newer, then remove the one that isn't newer.
                removed_elements.append({
                    **entry,  # Include all fields from the new lead
                    "reason": reason + " (older entry)"
                })
        else:
            # Add the entry to seen to not include it in the next iteration
            seen_elements.append(entry)

    # Return both seen and removed elements.
    return seen_elements, removed_elements

'''
The save_to_file function takes two parameters - a filename indicative of the file to
save to, and the data to write to the file. It assumes that data for the file is of JSON,
and utilizes the `dump` function from the `json` library to print it.
'''
def save_to_file(filename, data):
    # Print the data to the file that is UTF-8 encoded.
    with open(filename, 'w', encoding='utf-8') as output_file:
        # Data is a list of dictionaries, directly serialize it
        json.dump(data, output_file, indent=4)

'''
The main function executes the program. It expects one parameter, the filename to clean.
Should the user not include the filename, it will exit out as it requires a filename to 
run. The function then loads the JSON data from the filename, expecting it to have a
top level entry called `leads` that contains the JSON elements. It deduplicates the elements
based on the requirements given, and then saves these to two files called cleaned_{filename}.json
and removed_{filename}.json, where {filename} represents the original filename passed in. For example
for a file called `leads.json`, the output filenames are `removed_leads.json` and `cleaned_leads.json`.

Should any exceptions occur during this function, the code will handle it gracefully through the use
of a try/catch block, and print the error out.
'''
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <filename>")
        return

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as file:
            data = json.load(file)

        if 'leads' not in data or not isinstance(data['leads'], list):
            print("Error: JSON file must contain a 'leads' key with a list of objects.")
            return

        leads = data['leads']

        deduplicated_data, removed_data = remove_duplicates(leads)

        # Write the cleaned data back to a new file
        output_filename = f"cleaned_{filename}"
        save_to_file(output_filename, deduplicated_data)

        # Write the removed data to a separate file
        removed_filename = f"removed_{filename}"
        save_to_file(removed_filename, removed_data)

        print(f"Duplicates removed. Cleaned data saved to {output_filename}")
        print(f"Removed data saved to {removed_filename}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()