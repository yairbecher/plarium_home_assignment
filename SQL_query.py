query = """WITH CampaignData AS (
    SELECT
        Registration_Date,
        Campaign_ID,
        Country,
        Advertising_Channel,
        Advertising_Spend,
        Registrations
    FROM Campaigns
),
UserData AS (
    SELECT
        Registration_Date,
        Registration_ID,
        Campaign_ID,
        Country,
        Day7_Deposit_Amount,
        Day30_Deposit_Amount,
        Day60_Deposit_Amount,
        Day90_Deposit_Amount,
        Day120_Deposit_Amount,
        Day150_Deposit_Amount,
        Day180_Deposit_Amount
    FROM User
)
SELECT 
    c.Registration_Date,
    c.Campaign_ID,
    c.Country,
    c.Advertising_Channel,
    c.Advertising_Spend,
    c.Registrations,
    COUNT(u.Registration_ID) AS Registered_Users,
    COALESCE(SUM(u.Day7_Deposit_Amount), 0) AS Total_Day7_Revenue,
    COALESCE(SUM(u.Day30_Deposit_Amount), 0) AS Total_Day30_Revenue,
    COALESCE(SUM(u.Day60_Deposit_Amount), 0) AS Total_Day60_Revenue,
    COALESCE(SUM(u.Day90_Deposit_Amount), 0) AS Total_Day90_Revenue,
    COALESCE(SUM(u.Day120_Deposit_Amount), 0) AS Total_Day120_Revenue,
    COALESCE(SUM(u.Day150_Deposit_Amount), 0) AS Total_Day150_Revenue,
    COALESCE(SUM(u.Day180_Deposit_Amount), 0) AS Total_Day180_Revenue
FROM CampaignData c
LEFT JOIN UserData u 
    ON c.Campaign_ID = u.Campaign_ID 
    AND c.Registration_Date = u.Registration_Date 
    AND c.Country = u.Country
GROUP BY c.Registration_Date, c.Campaign_ID, c.Country, c.Advertising_Channel, c.Advertising_Spend, c.Registrations
ORDER BY c.Registration_Date, c.Country, c.Campaign_ID;"""