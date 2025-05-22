CREATE TABLE IF NOT EXISTS Stocks (
-- This table stores general information about the stocks being traded.
    stock_id        SERIAL PRIMARY KEY,             -- Unique identifier for each stock
    symbol          VARCHAR(10) NOT NULL UNIQUE,    -- Trading symbol (e.g., AAPL, MSFT)
    company_name    VARCHAR(255) NOT NULL,          -- Full company name
    exchange        VARCHAR(50),                    -- Exchange where the stock is primarily traded (e.g., NASDAQ, NYSE)
    sector          VARCHAR(100),                   -- Industry sector
    industry        VARCHAR(100),                   -- Specific industry
    currency        VARCHAR(5) DEFAULT 'USD',       -- Currency of the stock (e.g., USD, EUR)
    isin            VARCHAR(12) UNIQUE,             -- International Securities Identification Number (optional)
    CONSTRAINT      chk_symbol_uppercase CHECK (symbol = UPPER(symbol)) -- Ensure symbol is uppercase
);