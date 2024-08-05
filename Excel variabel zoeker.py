import pandas as pd
import os
import re
import csv
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw = file.read(10000)
    return chardet.detect(raw)['encoding']

def safe_contains(series, pat):
    try:
        return series.astype(str).str.contains(re.escape(pat), case=False, na=False)
    except Exception as e:
        print(f"Error in safe_contains: {e}")
        return pd.Series([False] * len(series))

def read_csv_safely(file_path):
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', detect_encoding(file_path)]
    separators = [',', ';', '\t', '|']
    
    for encoding in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(file_path, encoding=encoding, sep=sep, low_memory=False)
                print(f"  Succesvol geladen met encoding: {encoding} en separator: {sep}")
                return df
            except Exception as e:
                pass
    
    print(f"  Kon het bestand niet lezen met de beschikbare methoden.")
    return None

# Lees de data-dictionary
data_dictionary = pd.read_excel(r'C:\Users\sanma\Downloads\PORSCH\GP_new.xlsx')
print(f"Data dictionary geladen. Aantal rijen: {len(data_dictionary)}")

# Maak een kopie van de data-dictionary
result_dictionary = data_dictionary.copy()

# Voeg een nieuwe kolom toe voor de bestandsnamen, geïnitialiseerd met een lege string
result_dictionary['Bestandsnaam'] = ''

# Pad naar de map met de CSV-bestanden
csv_map = r"C:\Users\sanma\Downloads\PORSCH\PORSCH pancreas map"

# Toon alle bestanden in de map
print("\nAlle bestanden in de map:")
for filename in os.listdir(csv_map):
    print(filename)

# Teller voor verwerkte bestanden
processed_files = 0

# Loop door alle CSV-bestanden in de map
for filename in os.listdir(csv_map):
    if filename.endswith('.csv'):  # Controleer of het een CSV-bestand is
        file_path = os.path.join(csv_map, filename)
        print(f"\nVerwerken van bestand: {filename}")
        
        df = read_csv_safely(file_path)
        if df is not None:
            print(f"  Bestand geladen. Kolommen: {', '.join(df.columns)}")
            
            # Teller voor overeenkomsten in dit bestand
            matches_in_file = 0
            
            # Controleer elke variabele in de data-dictionary
            for index, row in result_dictionary.iterrows():
                variabele = row['Variable name']  # Zorg ervoor dat deze kolomnaam correct is
                
                # Zoek de variabele in de kolomkoppen
                if any(safe_contains(pd.Series(df.columns), variabele)):
                    matches_in_file += 1
                    if result_dictionary.at[index, 'Bestandsnaam']:
                        # Voeg de nieuwe bestandsnaam toe aan de lijst als deze nog niet aanwezig is
                        current_files = result_dictionary.at[index, 'Bestandsnaam'].split(', ')
                        if filename not in current_files:
                            result_dictionary.at[index, 'Bestandsnaam'] += f', {filename}'
                    else:
                        result_dictionary.at[index, 'Bestandsnaam'] = filename
            
            print(f"  Aantal overeenkomsten gevonden in {filename}: {matches_in_file}")
            processed_files += 1
        else:
            print(f"  Kon het bestand niet verwerken: {filename}")

# Toon statistieken
print(f"\nVerwerking voltooid. {processed_files} bestanden verwerkt.")
print(f"Aantal rijen met gevonden bestandsnamen: {result_dictionary['Bestandsnaam'].notna().sum()}")

# Sla het resultaat op in een nieuw Excel-bestand
output_path = r"C:\Users\sanma\Downloads\PORSCH\nieuwe_data_dictionary.xlsx"
result_dictionary.to_excel(output_path, index=False)
print(f"Nieuw bestand opgeslagen als: {output_path}")

# Toon enkele voorbeeldrijen
print("\nVoorbeeldrijen uit het resultaat:")
print(result_dictionary[['Variable name', 'Bestandsnaam']].head())

# Toon rijen zonder bestandsnaam
print("\nVoorbeelden van rijen zonder bestandsnaam:")
print(result_dictionary[result_dictionary['Bestandsnaam'] == ''][['Variable name', 'Bestandsnaam']].head())