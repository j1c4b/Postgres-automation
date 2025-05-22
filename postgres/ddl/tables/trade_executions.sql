CREATE TABLE IF NOT EXISTS TradeExecutions (
-- This is the core table that records each individual trade execution.
    trade_id SERIAL PRIMARY KEY, -- Unique identifier for each trade execution
    account_id INT NOT NULL, -- Foreign key referencing the Accounts table
    stock_id INT NOT NULL, -- Foreign key referencing the Stocks table
    broker_id INT, -- Redundant but useful for quick queries on broker (can be derived from account_id too)
    trade_type VARCHAR(10) NOT NULL, -- 'BUY' or 'SELL'
    quantity NUMERIC(15, 4) NOT NULL CHECK (quantity > 0), -- Number of shares traded
    price NUMERIC(18, 4) NOT NULL CHECK (price > 0), -- Price per share at execution
    execution_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Exact timestamp of execution (UTC recommended)
    settlement_date DATE, -- Date the trade is settled (T+2 for stocks)
    commission NUMERIC(10, 4) DEFAULT 0.00, -- Commission paid for the trade
    fees NUMERIC(10, 4) DEFAULT 0.00, -- Other fees associated with the trade
    total_amount NUMERIC(18, 4) GENERATED ALWAYS AS ((quantity * price) + commission + fees) STORED, -- Calculated total amount
    currency VARCHAR(5) DEFAULT 'USD', -- Currency of the trade (can be different from stock currency if FX conversion happened)
    order_id VARCHAR(50), -- Optional: ID from the order management system
    execution_status VARCHAR(20) DEFAULT 'EXECUTED', -- e.g., 'EXECUTED', 'CANCELLED', 'REJECTED'
    notes TEXT, -- Any additional notes about the trade
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the record was created
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the record was last updated

    CONSTRAINT fk_account
        FOREIGN KEY (account_id)
        REFERENCES Accounts (account_id)
        ON DELETE RESTRICT, -- Prevent deleting an account if trades are linked to it
    CONSTRAINT fk_stock
        FOREIGN KEY (stock_id)
        REFERENCES Stocks (stock_id)
        ON DELETE RESTRICT, -- Prevent deleting a stock if trades are linked to it
    CONSTRAINT fk_broker_trade -- Optional: Link to broker directly for convenience
        FOREIGN KEY (broker_id)
        REFERENCES Brokers (broker_id)
        ON DELETE SET NULL,
    CONSTRAINT chk_trade_type CHECK (trade_type IN ('BUY', 'SELL'))
);

-- Indexes for performance on frequently queried columns
CREATE INDEX IF NOT EXISTS idx_tradeexecutions_account_id ON TradeExecutions (account_id);
CREATE INDEX IF NOT EXISTS idx_tradeexecutions_stock_id ON TradeExecutions (stock_id);
CREATE INDEX IF NOT EXISTS idx_tradeexecutions_execution_timestamp ON TradeExecutions (execution_timestamp);
CREATE INDEX IF NOT EXISTS idx_tradeexecutions_trade_type ON TradeExecutions (trade_type);
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON Stocks (symbol);

-- Trigger to update 'updated_at' column automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tradeexecutions_updated_at
BEFORE UPDATE ON TradeExecutions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


