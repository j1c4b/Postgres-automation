CREATE TABLE IF NOT EXISTS Brokers (
    
    broker_id SERIAL PRIMARY KEY, -- Unique identifier for each broker
    broker_name VARCHAR(100) NOT NULL UNIQUE, -- Name of the brokerage firm
    contact_person VARCHAR(100), -- Primary contact at the brokerage
    contact_email VARCHAR(255), -- Contact email address
    phone_number VARCHAR(20), -- Contact phone number
    address TEXT -- Brokerage address
);