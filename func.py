import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns
import os
from scipy.signal import savgol_filter






input_file = os.environ.get('input_file')
df = pd.read_csv(input_file)




def convert_excel_date(date):
   excel_start = datetime(1899, 12, 30)
   try:
       number = int(date)
       date = excel_start + timedelta(days=number)
       return date.strftime('%m/%d/%Y')
   except ValueError:
       date = pd.to_datetime(date)
       return date.strftime('%m/%d/%Y')


def reformat_date(df: pd.DataFrame) -> pd.DataFrame:
   df['Registration_Date'] = df['Registration_Date'].apply(convert_excel_date)
   df['Registration_Date'] = pd.to_datetime(df['Registration_Date'], errors='coerce', dayfirst=False)
   return df


def calc_avg_deposits_df(df: pd.DataFrame):


   number_columns_dict = {
       'Number_Day7_Depositors': 'day_7',
       'Number_Day30_Depositors': 'day_30',
       'Number_Day60_Depositors': 'day_60',
       'Number_Day90_Depositors': 'day_90',
       'Number_Day120_Depositors': 'day_120',
       'Number_Day150_Depositors': 'day_150',
       'Number_Day180_Depositors': 'day_180'
   }


   amount_columns_dict = {
       'Accum_Day7_Deposit_Amount': 'day_7',
       'Accum_Day30_Deposit_Amount': 'day_30',
       'Accum_Day60_Deposit_Amount': 'day_60',
       'Accum_Day90_Deposit_Amount': 'day_90',
       'Accum_Day120_Deposit_Amount': 'day_120',
       'Accum_Day150_Deposit_Amount': 'day_150',
       'Accum_Day180_Deposit_Amount': 'day_180'
   }


   df_number = df.rename(columns=number_columns_dict)
   df_amount = df.rename(columns=amount_columns_dict)


   return df_number, df_amount






def calc_df_avg_Depositors_by_country(df: pd.DataFrame, conn):
   df.to_sql("game", conn, if_exists="replace", index=False)
   query = """SELECT
   Registration_Country,
   AVG(day_7) as avg_day7,
   AVG(day_30) - AVG(day_7) as avg_day30,
   AVG(day_60) - AVG(day_30) as avg_day60,
   AVG(day_90) - AVG(day_60) as avg_day90,
   AVG(day_120) - AVG(day_90) as avg_day120,
   AVG(day_150) - AVG(day_120) as avg_day150,
   AVG(day_180) - AVG(day_150) as avg_day180
FROM game
GROUP BY Registration_Country


UNION ALL


SELECT
   'Total Average' as Registration_Country,
   AVG(day_7) as avg_day7,
   AVG(day_30) - AVG(day_7) as avg_day30,
   AVG(day_60) - AVG(day_30) as avg_day60,
   AVG(day_90) - AVG(day_60) as avg_day90,
   AVG(day_120) - AVG(day_90) as avg_day120,
   AVG(day_150) - AVG(day_120) as avg_day150,
   AVG(day_180) - AVG(day_150) as avg_day180


FROM game"""
   result = pd.read_sql_query(query, conn)
   result.columns = ["Registration_Country", "avg_day7", "avg_day30", "avg_day60", "avg_day90",
                     "avg_day120", "avg_day150", "avg_day180"]

   return result






def avg_depositors_graph(df: pd.DataFrame, titel: str):


       df = df.set_index(df.columns[0])


       plt.figure(figsize=(10, 5))


       for country in df.index:
           plt.plot(df.columns, df.loc[country], marker='o', label=country)


       plt.xlabel('Days Range')
       plt.ylabel('Average')
       plt.title(f'Average {titel} Depositors Over Time by Country')
       plt.legend()
       plt.grid(True)
       plt.show()




def calc_df_avg_Depositors_by_channel(df: pd.DataFrame, conn):
   df.to_sql("game", conn, if_exists="replace", index=False)
   query = """SELECT
   Advertising_Channel,
   AVG(day_7) as avg_day7,
   AVG(day_30) - AVG(day_7) as avg_day30,
   AVG(day_60) - AVG(day_30) as avg_day60,
   AVG(day_90) - AVG(day_60) as avg_day90,
   AVG(day_120) - AVG(day_90) as avg_day120,
   AVG(day_150) - AVG(day_120) as avg_day150,
   AVG(day_180) - AVG(day_150) as avg_day180
FROM game
GROUP BY Advertising_Channel"""


   result = pd.read_sql_query(query, conn)
   return result






def calc_df_advertising_by_date(df: pd.DataFrame, conn):
   df.to_sql("game", conn, if_exists="replace", index=False)


   query = """SELECT
   strftime('%Y-%m', DATE(Registration_Date)) AS Month,
   Advertising_Channel,
   AVG(Advertising_Spend) AS avg_ad_spend,
   AVG(Number_Registrations) AS avg_registrations
FROM game
GROUP BY Month, Advertising_Channel
ORDER BY Month, Advertising_Channel;
"""


   result = pd.read_sql_query(query, conn)
   return result


def calc_advertising_by_channel_graphs(df_advertising: pd.DataFrame, output_dir):
   output_path = os.path.join(output_dir, "advertising_spend_over_time.png")


   df_advertising["Month"] = pd.to_datetime(df_advertising["Month"])


   # Plot 1: Advertising Spend Over Time by Channel
   plt.figure(figsize=(12, 6))
   for channel in df_advertising["Advertising_Channel"].unique():
       subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
       plt.plot(subset["Month"], subset["avg_ad_spend"], marker='o', label=channel)


   plt.xlabel("Month")
   plt.ylabel("Average Advertising Spend")
   plt.title("Advertising Spend Over Time by Channel")
   plt.legend()
   plt.grid(True)
   plt.xticks(rotation=45)
   plt.savefig(output_path, dpi=300)
   plt.show()


   # Plot 2: Registrations Over Time by Channel
   output_path = os.path.join(output_dir, "Registrations_Over_Time_by_Channel.png")


   plt.figure(figsize=(12, 6))
   for channel in df_advertising["Advertising_Channel"].unique():
       subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
       plt.plot(subset["Month"], subset["avg_registrations"], marker='o', label=channel)


   plt.xlabel("Month")
   plt.ylabel("Average Registrations")
   plt.title("Registrations Over Time by Channel")
   plt.legend()
   plt.grid(True)
   plt.xticks(rotation=45)
   plt.savefig(output_path, dpi=300)
   plt.show()




def calc_roi_per_channel(df: pd.DataFrame, conn):

    df.to_sql("game", conn, if_exists="replace", index=False)


    query = """WITH RankedData AS (
               SELECT
                   Advertising_Channel,
                   SUM(Advertising_Spend) AS total_ad_spend,
                   SUM(Number_Registrations) AS total_registrations,
                   (SUM(Accum_Day7_Deposit_Amount) - SUM(Advertising_Spend)) / SUM(Advertising_Spend) * 100 AS ROI_7,
                   (SUM(Accum_Day30_Deposit_Amount) - SUM(Advertising_Spend)) / SUM(Advertising_Spend) * 100 AS ROI_30,
                   (SUM(Accum_Day60_Deposit_Amount) - SUM(Advertising_Spend)) / SUM(Advertising_Spend) * 100 AS ROI_60,
                   (SUM(Accum_Day90_Deposit_Amount) - SUM(Advertising_Spend)) / SUM(Advertising_Spend) * 100 AS ROI_90,
                   (SUM(Accum_Day120_Deposit_Amount) - SUM(Advertising_Spend)) / SUM(Advertising_Spend) * 100 AS ROI_120,
                   (SUM(Accum_Day150_Deposit_Amount) - SUM(Advertising_Spend)) / SUM(Advertising_Spend) * 100 AS ROI_150,
                   (SUM(Accum_Day180_Deposit_Amount) - SUM(Advertising_Spend)) / SUM(Advertising_Spend) * 100 AS ROI_180
               FROM game
               GROUP BY Advertising_Channel
           )
           SELECT
               Advertising_Channel,
               ROI_7, ROI_30, ROI_60, ROI_90, ROI_120, ROI_150, ROI_180,
               RANK() OVER (ORDER BY total_ad_spend DESC) AS Rank_Ad_Spend,
               RANK() OVER (ORDER BY total_registrations DESC) AS Rank_Registrations
           FROM RankedData
           ORDER BY Rank_Ad_Spend;"""


    result = pd.read_sql_query(query, conn)
    return result



# def calc_roi_per_channel(df: pd.DataFrame, conn):
#     """
#     Calculates ROI per advertising channel, ranks channels by advertising spend & registrations,
#     and ensures proper formatting and handling of missing values.
#     """
#
#     # Ensure numeric columns have no NaNs before converting to int
#     df[["Advertising_Spend", "Number_Registrations",
#         "Accum_Day7_Deposit_Amount", "Accum_Day30_Deposit_Amount",
#         "Accum_Day60_Deposit_Amount", "Accum_Day90_Deposit_Amount",
#         "Accum_Day120_Deposit_Amount", "Accum_Day150_Deposit_Amount",
#         "Accum_Day180_Deposit_Amount"]] = df[[
#         "Advertising_Spend", "Number_Registrations",
#         "Accum_Day7_Deposit_Amount", "Accum_Day30_Deposit_Amount",
#         "Accum_Day60_Deposit_Amount", "Accum_Day90_Deposit_Amount",
#         "Accum_Day120_Deposit_Amount", "Accum_Day150_Deposit_Amount",
#         "Accum_Day180_Deposit_Amount"
#     ]].fillna(0).astype(int)
#
#     # Debugging: Print the first few rows to confirm correct conversion
#     print("🚀 DataFrame before inserting into SQL:")
#     print(df.head())
#
#     # Insert DataFrame into SQLite
#     df.to_sql("game", conn, if_exists="replace", index=False)
#
#     # Check if the table is empty
#     cursor = conn.cursor()
#     cursor.execute("SELECT COUNT(*) FROM game")
#     row_count = cursor.fetchone()[0]
#     if row_count == 0:
#         print("⚠️ No data found in SQL table. Returning empty DataFrame.")
#         return pd.DataFrame()
#
#     # SQL Query: Calculate ROI and rank advertising channels
#     query = """WITH RankedData AS (
#        SELECT
#            Advertising_Channel,
#            SUM(Advertising_Spend) AS total_ad_spend,
#            SUM(Number_Registrations) AS total_registrations,
#            COALESCE(SUM(Accum_Day7_Deposit_Amount), 0) AS total_deposit_day7,
#            COALESCE(SUM(Accum_Day30_Deposit_Amount), 0) AS total_deposit_day30,
#            COALESCE(SUM(Accum_Day60_Deposit_Amount), 0) AS total_deposit_day60,
#            COALESCE(SUM(Accum_Day90_Deposit_Amount), 0) AS total_deposit_day90,
#            COALESCE(SUM(Accum_Day120_Deposit_Amount), 0) AS total_deposit_day120,
#            COALESCE(SUM(Accum_Day150_Deposit_Amount), 0) AS total_deposit_day150,
#            COALESCE(SUM(Accum_Day180_Deposit_Amount), 0) AS total_deposit_day180,
#
#            -- ROI Calculation with NULL handling
#            COALESCE(
#                CASE
#                    WHEN SUM(Advertising_Spend) = 0 THEN NULL
#                    ELSE (SUM(Accum_Day7_Deposit_Amount) - SUM(Advertising_Spend)) / NULLIF(SUM(Advertising_Spend), 0) * 100
#                END, 0) AS ROI_7,
#
#            COALESCE(
#                CASE
#                    WHEN SUM(Advertising_Spend) = 0 THEN NULL
#                    ELSE (SUM(Accum_Day30_Deposit_Amount) - SUM(Advertising_Spend)) / NULLIF(SUM(Advertising_Spend), 0) * 100
#                END, 0) AS ROI_30,
#
#            COALESCE(
#                CASE
#                    WHEN SUM(Advertising_Spend) = 0 THEN NULL
#                    ELSE (SUM(Accum_Day60_Deposit_Amount) - SUM(Advertising_Spend)) / NULLIF(SUM(Advertising_Spend), 0) * 100
#                END, 0) AS ROI_60,
#
#            COALESCE(
#                CASE
#                    WHEN SUM(Advertising_Spend) = 0 THEN NULL
#                    ELSE (SUM(Accum_Day90_Deposit_Amount) - SUM(Advertising_Spend)) / NULLIF(SUM(Advertising_Spend), 0) * 100
#                END, 0) AS ROI_90,
#
#            COALESCE(
#                CASE
#                    WHEN SUM(Advertising_Spend) = 0 THEN NULL
#                    ELSE (SUM(Accum_Day120_Deposit_Amount) - SUM(Advertising_Spend)) / NULLIF(SUM(Advertising_Spend), 0) * 100
#                END, 0) AS ROI_120,
#
#            COALESCE(
#                CASE
#                    WHEN SUM(Advertising_Spend) = 0 THEN NULL
#                    ELSE (SUM(Accum_Day150_Deposit_Amount) - SUM(Advertising_Spend)) / NULLIF(SUM(Advertising_Spend), 0) * 100
#                END, 0) AS ROI_150,
#
#            COALESCE(
#                CASE
#                    WHEN SUM(Advertising_Spend) = 0 THEN NULL
#                    ELSE (SUM(Accum_Day180_Deposit_Amount) - SUM(Advertising_Spend)) / NULLIF(SUM(Advertising_Spend), 0) * 100
#                END, 0) AS ROI_180
#
#        FROM game
#        GROUP BY Advertising_Channel
#     )
#     SELECT
#        Advertising_Channel,
#        ROI_7, ROI_30, ROI_60, ROI_90, ROI_120, ROI_150, ROI_180,
#        RANK() OVER (ORDER BY total_ad_spend DESC) AS Rank_Ad_Spend,
#        RANK() OVER (ORDER BY total_registrations DESC) AS Rank_Registrations
#     FROM RankedData
#     ORDER BY Rank_Ad_Spend;"""
#
#     # Execute the SQL query
#     result = pd.read_sql_query(query, conn)
#
#     # Standardize column names (strip spaces)
#     result.columns = result.columns.str.strip()
#
#     # Define the expected ROI columns
#     roi_columns = ["ROI_7", "ROI_30", "ROI_60", "ROI_90", "ROI_120", "ROI_150", "ROI_180"]
#
#     # Check if the expected ROI columns exist
#     existing_cols = [col for col in roi_columns if col in result.columns]
#
#     if existing_cols:
#         # Convert existing ROI columns to integers
#         result[existing_cols] = result[existing_cols].fillna(0).astype(int)
#     else:
#         print("⚠️ Warning: No ROI columns found in result.")
#
#     return result


def plot_all_channels_side_by_side(df_advertising: pd.DataFrame):


   channels = df_advertising["Advertising_Channel"].unique()
   num_channels = len(channels)


   # Define grid layout: Each channel gets 2 plots (side by side), so 2 columns
   rows = num_channels  # Each row represents one advertising channel
   cols = 2  # Two columns: one for ad spend, one for registrations


   # Create figure with subplots
   fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(15, 5 * rows), sharex=True)


   # Loop through each advertising channel and plot both metrics
   for idx, channel in enumerate(channels):
       subset = df_advertising[df_advertising["Advertising_Channel"] == channel]


       # Left plot: Advertising Spend Over Time
       axes[idx, 0].plot(subset["Month"], subset["avg_ad_spend"], marker='o', linestyle='-', color="blue")
       axes[idx, 0].set_title(f"Ad Spend - {channel}")
       axes[idx, 0].set_ylabel("Avg Ad Spend")
       axes[idx, 0].grid(True)


       # Right plot: Registrations Over Time
       axes[idx, 1].plot(subset["Month"], subset["avg_registrations"], marker='o', linestyle='-', color="green")
       axes[idx, 1].set_title(f"Registrations - {channel}")
       axes[idx, 1].set_ylabel("Avg Registrations")
       axes[idx, 1].grid(True)


   # Formatting
   plt.xticks(rotation=45)
   plt.tight_layout()


   # # Save figure
   # output_path = os.path.join(output_dir, "All_Channels_AdSpend_vs_Registrations.png")
   # plt.savefig(output_path, dpi=300)
   plt.show()




#
#
# def plot_advertising_vs_registrations_subplots(df_advertising: pd.DataFrame):
#
#     for channel in df_advertising["Advertising_Channel"].unique():
#         subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
#
#         fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 10), sharex=True)
#
#         axes[0].plot(subset["Month"], subset["avg_ad_spend"], marker='o', linestyle='-', color="blue")
#         axes[0].set_ylabel("Avg Ad Spend")
#         axes[0].set_title(f"Advertising Spend Over Time - {channel}")
#         axes[0].grid(True)
#
#         axes[1].plot(subset["Month"], subset["avg_registrations"], marker='o', linestyle='-', color="green")
#         axes[1].set_ylabel("Avg Registrations")
#         axes[1].set_xlabel("Month")
#         axes[1].set_title(f"Registrations Over Time - {channel}")
#         axes[1].grid(True)
#
#         plt.xticks(rotation=45)
#         plt.tight_layout()
#
#         # # Save plot
#         # output_path = os.path.join(output_dir, f"{channel.replace(' ', '_')}_ad_vs_registrations_subplot.png")
#         # plt.savefig(output_path, dpi=300)
#         plt.show()
#
#


#
# def plot_percentage_change_graph(df: pd.DataFrame, column: str, ylabel: str, title: str, output_path: str):
#     """
#     פונקציה כללית להכנת גרף של שינוי באחוזים לאורך זמן לפי ערוץ.
#     """
#     plt.figure(figsize=(12, 6))
#
#     for channel in df["Advertising_Channel"].unique():
#         subset = df[df["Advertising_Channel"] == channel]
#         color = "gray" if channel in df["low_variance_channels"].values else None  # צביעת ערוצים סטטיים
#         trend = savgol_filter(subset[column].fillna(0), window_length=5, polyorder=2, mode="nearest")
#
#         plt.plot(subset["Month"], subset[column], label=channel, alpha=0.6, color=color)
#         plt.plot(subset["Month"], trend, linestyle="dashed", color=color if color else "black")  # קו מגמה
#
#     plt.xlabel("Month")
#     plt.ylabel(ylabel)
#     plt.title(title)
#     plt.legend()
#     plt.grid(True)
#     plt.xticks(rotation=45)
#     plt.savefig(output_path, dpi=300)
#     plt.show()
#
#
# def calc_advertising_by_channel_graphs(df_advertising: pd.DataFrame, output_dir: str):
#     """
#     פונקציה המחוללת גרפים של שינוי באחוזים בפרסום ובהרשמות לפי ערוץ לאורך זמן.
#     """
#     os.makedirs(output_dir, exist_ok=True)  # יצירת תיקיית יעד אם היא לא קיימת
#
#     # המרת תאריכים
#     df_advertising["Month"] = pd.to_datetime(df_advertising["Month"])
#
#     # חישוב שינוי באחוזים
#     df_advertising = df_advertising.sort_values(by=["Advertising_Channel", "Month"])
#     df_advertising["pct_change_spend"] = df_advertising.groupby("Advertising_Channel")[
#                                              "avg_ad_spend"].pct_change() * 100
#     df_advertising["pct_change_registrations"] = df_advertising.groupby("Advertising_Channel")[
#                                                      "avg_registrations"].pct_change() * 100
#
#     # זיהוי ערוצים עם שינויים נמוכים (מתחת ל-5%)
#     low_variance_channels = df_advertising.groupby("Advertising_Channel")[
#         ["pct_change_spend", "pct_change_registrations"]].std()
#     low_variance_channels = low_variance_channels[
#         (low_variance_channels["pct_change_spend"] < 5) & (low_variance_channels["pct_change_registrations"] < 5)].index
#     df_advertising["low_variance_channels"] = df_advertising["Advertising_Channel"].apply(
#         lambda x: x if x in low_variance_channels else "")
#
#     # גרף הוצאות פרסום
#     plot_percentage_change_graph(
#         df_advertising,
#         column="pct_change_spend",
#         ylabel="Percentage Change in Ad Spend (%)",
#         title="Advertising Spend Percentage Change Over Time by Channel",
#         output_path=os.path.join(output_dir, "advertising_spend_percentage_change.png")
#     )
#
#     # גרף הרשמות
#     plot_percentage_change_graph(
#         df_advertising,
#         column="pct_change_registrations",
#         ylabel="Percentage Change in Registrations (%)",
#         title="Registrations Percentage Change Over Time by Channel",
#         output_path=os.path.join(output_dir, "registrations_percentage_change.png")
#     )
#
#






# def df_sttistic_for_number_depositors(conn):
#     query = """WITH statistics AS (
#     SELECT
#         AVG(Number_Day7_Depositors) as avg_7,
#         PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Number_Day7_Depositors) as median_7,
#         STDDEV(Number_Day7_Depositors) as stddev_7,
#
#         AVG(Number_Day30_Depositors) as avg_30,
#         PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Number_Day30_Depositors) as median_30,
#         STDDEV(Number_Day30_Depositors) as stddev_30,
#
#         AVG(Number_Day60_Depositors) as avg_60,
#         PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Number_Day60_Depositors) as median_60,
#         STDDEV(Number_Day60_Depositors) as stddev_60,
#
#         AVG(Number_Day90_Depositors) as avg_90,
#         PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Number_Day90_Depositors) as median_90,
#         STDDEV(Number_Day90_Depositors) as stddev_90,
#
#         AVG(Number_Day120_Depositors) as avg_120,
#         PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Number_Day120_Depositors) as median_120,
#         STDDEV(Number_Day120_Depositors) as stddev_120,
#
#         AVG(Number_Day150_Depositors) as avg_150,
#         PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Number_Day150_Depositors) as median_150,
#         STDDEV(Number_Day150_Depositors) as stddev_150,
#
#         AVG(Number_Day180_Depositors) as avg_180,
#         PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Number_Day180_Depositors) as median_180,
#         STDDEV(Number_Day180_Depositors) as stddev_180
#     FROM your_table_name
# )
# SELECT
#     'Average' as statistic_type,
#     avg_7 as Day7,
#     avg_30 as Day30,
#     avg_60 as Day60,
#     avg_90 as Day90,
#     avg_120 as Day120,
#     avg_150 as Day150,
#     avg_180 as Day180
# FROM statistics
#
# UNION ALL
#
# SELECT
#     'Median' as statistic_type,
#     median_7,
#     median_30,
#     median_60,
#     median_90,
#     median_120,
#     median_150,
#     median_180
# FROM statistics
#
# UNION ALL
#
# SELECT
#     'StdDev' as statistic_type,
#     stddev_7,
#     stddev_30,
#     stddev_60,
#     stddev_90,
#     stddev_120,
#     stddev_150,
#     stddev_180
# FROM statistics;"""
#
#     result = pd.read_sql_query(query, conn)
#     print(result)
#     return result


# Function to try multiple date formats
# def parse_dates(date_str, formats):
#     for fmt in formats:
#         try:
#             return pd.to_datetime(date_str, format=fmt, errors='raise')
#         except (ValueError, TypeError):
#             continue
#     return pd.NaT  # or return a default date, e.g., pd.Timestamp('2000-01-01')
#
# # Apply the function to the 'Registration_Date' column
# df['Registration_Date'] = df['Registration_Date'].apply(lambda x: parse_dates(x, formats))
#
# # Handle nulls (if any) in a way that makes sense for your analysis
# df['Registration_Date'].fillna(pd.Timestamp('2000-01-01'), inplace=True)
#
#
#
# # Check for missing values
# missing_dates = df["Registration_Date"].isna().sum()
# if missing_dates > 0:
#     print(f"Warning: {missing_dates} rows have invalid dates and will be dropped.")
# df = df.dropna(subset=["Registration_Date"])  # Remove invalid dates
#
# # Aggregate Data by Month
# df["Month"] = df["Registration_Date"].dt.to_period("M")  # Group by month
# monthly_trends = df.groupby("Month").agg({
#     "Number_Registrations": "sum",
#     "Advertising_Spend": "sum",
#     "Number_Day7_Depositors": "sum",
#     "Number_Day30_Depositors": "sum",
#     "Accum_Day30_Deposit_Amount": "sum"
# }).reset_index()
#
# # Convert Period to Datetime for plotting
# monthly_trends["Month"] = monthly_trends["Month"].astype(str)
# monthly_trends["Month"] = pd.to_datetime(monthly_trends["Month"])
#
# # Plot Trends
# plt.figure(figsize=(12, 6))
# sns.lineplot(data=monthly_trends, x="Month", y="Number_Registrations", label="Registrations", marker="o")
# sns.lineplot(data=monthly_trends, x="Month", y="Number_Day30_Depositors", label="Day30 Depositors", marker="s")
# sns.lineplot(data=monthly_trends, x="Month", y="Advertising_Spend", label="Ad Spend", marker="D")
#
# plt.axvline(pd.to_datetime("2023-09-01"), color="red", linestyle="--", label="Potential Change Point")
# plt.axvline(pd.to_datetime("2023-04-01"), color="blue", linestyle="--", label="Another Change Point")
#
# plt.xlabel("Month")
# plt.ylabel("Values (Scaled)")
# plt.title("Trend Analysis of Registrations, Deposits & Advertising Spend")
# plt.legend()
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()
#
# # Detect Monthly Percentage Changes
# monthly_trends["Reg_Change"] = monthly_trends["Number_Registrations"].pct_change() * 100
# monthly_trends["Dep_Change"] = monthly_trends["Number_Day30_Depositors"].pct_change() * 100
# monthly_trends["Ad_Change"] = monthly_trends["Advertising_Spend"].pct_change() * 100
#
# # Print Significant Changes (>10% increase or decrease)
# significant_changes = monthly_trends[
#     (monthly_trends["Reg_Change"].abs() > 10) |
#     (monthly_trends["Dep_Change"].abs() > 10) |
#     (monthly_trends["Ad_Change"].abs() > 10)
# ]
# print("\n🚀 Significant Trend Changes Detected:")
# print(significant_changes[["Month", "Reg_Change", "Dep_Change", "Ad_Change"]])

