import csv
import random
import datetime

makes = ["Ford", "Honda", "Toyota", "Chevrolet", "Nissan", "Hyundai", "BMW", "Mercedes", "Audi", "Jeep"]
models = {"Ford": ["F-150", "Mustang", "Escape"], "Honda": ["Civic", "CR-V", "Accord"], "Toyota": ["Camry", "RAV4", "Tacoma"], "Chevrolet":["Silverado", "Traverse", "Equinox"], "Nissan":["Rogue", "Altima", "Titan"], "Hyundai":["Sonata", "Tucson", "Elantra"], "BMW":["X5", "3 Series", "5 Series"], "Mercedes":["C-Class", "E-Class", "S-Class"], "Audi":["A4", "Q5", "A6"], "Jeep":["Wrangler", "Grand Cherokee", "Cherokee"]}
colors = ["Red", "Blue", "Silver", "Black", "White", "Gray", "Green"]
types = ["Truck", "Sedan", "SUV", "Coupe"]
engines = ["2.0L I4", "2.5L I4", "3.5L V6", "3.6L V6", "5.0L V8"]
transmissions = ["Automatic", "CVT", "Manual"]
locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
salespeople = list(range(101,121))

with open('car_sales.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["SalesID","Date","CustomerName","CustomerPhone","CustomerEmail","VehicleMake","VehicleModel","VehicleYear","VehicleColor","VehicleType","VehicleMileage","VehicleEngine","VehicleTransmission","SalePrice","SaleType","SalespersonID","DealershipLocation","FinancingApproved","DownPayment","LoanTerm"])
    for i in range(1, 5001):
        make = random.choice(makes)
        model = random.choice(models[make])
        year = random.randint(2018, 2024)
        mileage = random.randint(0 if year == 2024 else 5000, 60000)
        price = random.randint(15000, 60000)
        sale_type = random.choice(["New", "Used"])
        financing = random.choice([True, False])
        down_payment = random.randint(0, price // 4) if financing else 0
        loan_term = random.choice([0, 36, 48, 60, 72]) if financing else 0
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2024, 1, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)
        writer.writerow([i, random_date.strftime("%Y-%m-%d"), f"Customer {i}", f"555-{random.randint(100,999)}-{random.randint(1000,9999)}", f"customer{i}@email.com", make, model, year, random.choice(colors), random.choice(types), mileage, random.choice(engines), random.choice(transmissions), price, sale_type, random.choice(salespeople), random.choice(locations), financing, down_payment, loan_term])
print("CSV file 'car_sales.csv' created successfully.")