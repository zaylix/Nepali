import json
import random
import os
import sqlite3

# Data Sources
MALE_NAMES = ["Ram", "Shyam", "Hari", "Bijay", "Sanjay", "Hemant", "Prakash", "Deepak", "Sandesh", "Rohan", "Aayush", "Bishal", "Kiran", "Nabin", "Suman", "Rajesh", "Suresh", "Gopal", "Parshu", "Manoj", "Arjun", "Krishna", "Santosh", "Dinesh", "Bharat", "Kushal", "Prabhat", "Sagar", "Anil", "Sunil"]
FEMALE_NAMES = ["Sita", "Gita", "Rita", "Sunita", "Anita", "Pabitra", "Nirmala", "Kabita", "Maya", "Sushma", "Rupa", "Deepa", "Anju", "Manju", "Sarita", "Bimala", "Kamala", "Radha", "Sabitri", "Indira", "Kalpana", "Shanti", "Laxmi", "Saraswati", "Tara", "Urmila", "Parbati", "Januka", "Mina", "Sabina"]
SURNAMES = ["Sharma", "Adhikari", "Bhattarai", "Khatri", "Thapa", "Magar", "Gurung", "Rai", "Limbu", "Shrestha", "Maharjan", "Bajracharya", "Pandey", "Paudel", "Gautam", "Basnet", "Yadav", "Shah", "Singh", "Jha", "Khadka", "Mishra", "Acharya", "Dahal", "Koirala", "Oli", "Bhandari", "Lamsal", "Regmi", "Subedi", "Aryal", "Neupane", "Ghimire", "Bastola", "Baniya", "Bohara", "Budhathoki", "Chhetri", "Dhakal", "Karki", "Kunwar", "Lamichhane", "Mainali", "Pant", "Prasai", "Pyakurel", "Rana", "Rimal", "Sapkota", "Silwal", "Upreti", "Wagle"]
MALE_MIDDLE_NAMES = ["Bahadur", "Prasad", "Kumar", "Raj", "Lal", "Nath", "Singh", "Giri", "Chandra", "Man", "Kanta"]
FEMALE_MIDDLE_NAMES = ["Kumari", "Devi", "Maya", "Sari", "Laxmi", "Shanti"]
DISTRICTS = ["Kathmandu", "Kaski", "Lalitpur", "Chitwan", "Morang", "Parsa", "Dhanusa", "Dang", "Makwanpur", "Kailali", "Sunsari", "Rupandehi", "Banke", "Jhapa", "Illam", "Bardiya", "Surkhet", "Baglung", "Gorkha", "Syangja", "Tanahun", "Nawalpur", "Parbat", "Myagdi", "Mustang", "Dolpa", "Mugu", "Humla", "Jumla", "Kalikot", "Dailekh", "Jajarkot", "Salyan", "Pyuthan", "Rolpa", "Rukum", "Gulmi", "Arghakhanchi", "Palpa", "Kapilvastu", "Saptari", "Siraha", "Udayapur", "Okhaldhunga", "Khotang", "Solukhumbu", "Sankhuwasabha", "Bhojpur", "Dhankuta", "Tehrathum", "Panchthar", "Taplejung"]

def generate_realistic_entry(mobile):
    gender = random.choice(["Male", "Female"])
    lname = random.choice(SURNAMES)
    
    if gender == "Male":
        fname_base = random.choice(MALE_NAMES)
        mname = random.choice(MALE_MIDDLE_NAMES) if random.random() < 0.4 else ""
    else:
        fname_base = random.choice(FEMALE_NAMES)
        mname = random.choice(FEMALE_MIDDLE_NAMES) if random.random() < 0.4 else ""
    
    fname = f"{fname_base} {mname}".strip()
    name = f"{fname} {lname}"
    
    district = random.choice(DISTRICTS)
    ward = random.randint(1, 32)
    
    prefix = mobile[:3]
    circle = "NTC" if prefix in ["984", "985", "986", "974", "975", "976", "972"] else "NCELL"
    
    entry = {
        "name": name,
        "fname": fname,
        "mobile": mobile,
        "circle": circle,
        "address": f"Ward No. {ward}, {district}, Nepal",
        "id": str(random.randint(100000000000, 999999999999)),
        "gender": gender,
        "dev": "@diwazz"
    }
    
    # Advanced fields with consistent logic
    if random.random() < 0.6:
        entry["email"] = f"{fname_base.lower()}.{lname.lower()}{random.randint(10, 999)}@gmail.com"
        
    if random.random() < 0.5:
        # Realistic Nagrita: DistrictCode-Year-Serial (e.g., 27-01-75-12345)
        entry["nagrita_no"] = f"{random.randint(10, 75)}-{random.randint(1, 15)}-{random.randint(60, 80)}-{random.randint(10000, 99999)}"
        entry["ward_no"] = str(ward)
        
    if random.random() < 0.4:
        # Father has same surname
        f_name_base = random.choice(MALE_NAMES)
        f_mname = random.choice(MALE_MIDDLE_NAMES) if random.random() < 0.5 else ""
        entry["father_name"] = f"{f_name_base} {f_mname} {lname}".replace("  ", " ").strip()
        
    if random.random() < 0.3:
        # Mother has same surname (married)
        m_name_base = random.choice(FEMALE_NAMES)
        m_mname = random.choice(FEMALE_MIDDLE_NAMES) if random.random() < 0.5 else ""
        entry["mother_name"] = f"{m_name_base} {m_mname} {lname}".replace("  ", " ").strip()

    return entry

def main():
    db_dir = "/home/ubuntu/Nepali-local/data_parts"
    os.makedirs(db_dir, exist_ok=True)
    
    # Target: 1GB+ (approx 4.5 million entries)
    total_entries = 4500000
    entries_per_part = 225000 # Approx 50MB per part
    
    prefixes = ["984", "985", "986", "974", "975", "976", "980", "981", "982"]
    
    print(f"Generating {total_entries} entries...")
    
    # Use SQLite for temporary storage to avoid memory issues
    conn = sqlite3.connect('temp_db.sqlite')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS data (mobile TEXT, json_data TEXT)')
    
    batch = []
    for i in range(total_entries):
        prefix = random.choice(prefixes)
        mobile = prefix + "".join([str(random.randint(0, 9)) for _ in range(7)])
        entry = generate_realistic_entry(mobile)
        batch.append((mobile, json.dumps(entry)))
        
        if len(batch) >= 10000:
            c.executemany('INSERT INTO data VALUES (?, ?)', batch)
            conn.commit()
            batch = []
            if (i + 1) % 100000 == 0:
                print(f"Generated {i + 1} entries...")

    # Export to JSON parts
    print("Exporting to JSON parts...")
    c.execute('SELECT json_data FROM data')
    part_idx = 1
    current_part_data = []
    
    while True:
        row = c.fetchone()
        if row:
            current_part_data.append(json.loads(row[0]))
            if len(current_part_data) >= entries_per_part:
                with open(f"{db_dir}/data_part{part_idx}.json", "w") as f:
                    json.dump(current_part_data, f)
                print(f"Saved part {part_idx}")
                part_idx += 1
                current_part_data = []
        else:
            if current_part_data:
                with open(f"{db_dir}/data_part{part_idx}.json", "w") as f:
                    json.dump(current_part_data, f)
            break
            
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
