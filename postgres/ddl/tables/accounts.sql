CREATE TABLE IF NOT EXISTS Accounts (
    
    account_id SERIAL PRIMARY KEY, -- Unique identifier for the trading account
    account_number VARCHAR(50) NOT NULL UNIQUE, -- User-defined account number
    broker_id INT, -- Foreign key referencing the Brokers table
    account_type VARCHAR(50), -- e.g., 'Individual', 'Joint', 'IRA', 'Margin'
    account_holder_name VARCHAR(255), -- Name of the primary account holder
    opening_date DATE DEFAULT CURRENT_DATE, -- Date the account was opened
    CONSTRAINT fk_broker
        FOREIGN KEY (broker_id)
        REFERENCES Brokers (broker_id)
        ON DELETE SET NULL -- If a broker is deleted, set broker_id in Accounts to NULL
);