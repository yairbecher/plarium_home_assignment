import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os


# # # prep # # #

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


# # # save # # #

def save_dataframes(output_dir, dataframes_dict):
    for name, df in dataframes_dict.items():
        file_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(file_path, index=False)
        print(f"Saved: {file_path}")


# def save_plots(output_dir, plots_dict):
#     for name, plot_func in plots_dict.items():
#         file_path = os.path.join(output_dir, f"{name}.png")
#         plt.figure()
#         plot_func()
#         plt.savefig(file_path)
#         plt.close()
#         print(f"Saved: {file_path}")

def save_plots(output_dir, plots_dict):
    for name, fig in plots_dict.items():
        file_path = os.path.join(output_dir, f"{name}.png")
        fig.savefig(file_path, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved: {file_path}")


def save_outputs(output_dir, dataframes_dict, plots_dict):
    save_dataframes(output_dir, dataframes_dict)
    save_plots(output_dir, plots_dict)
    print("All outputs saved successfully.")


# # # analasys # # #

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




# def avg_depositors_graph(df: pd.DataFrame, count: bool, by: bool, output_dir):
#
#        if count:
#            count = 'number'
#        else:
#            count = 'amount'
#
#        if by:
#            by = 'country'
#        else:
#            by = 'channel'
#
#        df = df.set_index(df.columns[0])
#
#        plt.figure(figsize=(10, 5))
#
#        for country in df.index:
#            plt.plot(df.columns, df.loc[country], marker='o', label=country)
#
#        plt.xlabel('Days Range')
#        plt.ylabel('Average')
#        plt.title(f'Average {count} Depositors Over Time by {by}')
#        plt.legend()
#        plt.grid(True)
#        plt.show()
#
#
#        file_path = os.path.join(output_dir, f'Average {count} Depositors Over Time by {by}')
#        fig.savefig(file_path, bbox_inches='tight')
#        print(f"Saved: {file_path}")
#        plt.close(fig)

def avg_depositors_graph(df: pd.DataFrame, count: bool, by: bool):
    count_label = 'number' if count else 'amount'
    by_label = 'country' if by else 'channel'
    df = df.set_index(df.columns[0])

    fig, ax = plt.subplots(figsize=(10, 5))
    for index in df.index:
        ax.plot(df.columns, df.loc[index], marker='o', label=index)

    ax.set_xlabel('Days Range')
    ax.set_ylabel('Average')
    ax.set_title(f'Average {count_label} Depositors Over Time by {by_label}')
    ax.legend()
    ax.grid(True)
    plt.show()

    return {f"avg_{count_label}_depositors_by_{by_label}": fig}


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

   return pd.read_sql_query(query, conn)




def calc_df_advertising_by_date(df: pd.DataFrame, conn):
   df.to_sql("game", conn, if_exists="replace", index=False)

   query = """SELECT
               strftime('%Y-%m', DATE(Registration_Date)) AS Month,
               Advertising_Channel,
               AVG(Advertising_Spend) AS avg_ad_spend,
               AVG(Number_Registrations) AS avg_registrations
            FROM game
            GROUP BY Month, Advertising_Channel
            ORDER BY Month, Advertising_Channel;"""

   return pd.read_sql_query(query, conn)


# def calc_advertising_by_channel_graphs(df_advertising: pd.DataFrame):
#    df_advertising["Month"] = pd.to_datetime(df_advertising["Month"])
#
#    # Plot 1
#    plt.figure(figsize=(12, 6))
#    for channel in df_advertising["Advertising_Channel"].unique():
#        subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
#        plt.plot(subset["Month"], subset["avg_ad_spend"], marker='o', label=channel)
#
#
#    plt.xlabel("Month")
#    plt.ylabel("Average Advertising Spend")
#    plt.title("Advertising Spend Over Time by Channel")
#    plt.legend()
#    plt.grid(True)
#    plt.xticks(rotation=45)
#    plt.show()
#
#
#    # Plot 2
#    plt.figure(figsize=(12, 6))
#    for channel in df_advertising["Advertising_Channel"].unique():
#        subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
#        plt.plot(subset["Month"], subset["avg_registrations"], marker='o', label=channel)
#
#
#    plt.xlabel("Month")
#    plt.ylabel("Average Registrations")
#    plt.title("Registrations Over Time by Channel")
#    plt.legend()
#    plt.grid(True)
#    plt.xticks(rotation=45)
#    plt.show()


def calc_advertising_by_channel_graphs(df_advertising: pd.DataFrame):
    df_advertising["Month"] = pd.to_datetime(df_advertising["Month"])
    plots = {}

    # Plot 1
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    for channel in df_advertising["Advertising_Channel"].unique():
        subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
        ax1.plot(subset["Month"], subset["avg_ad_spend"], marker='o', label=channel)

    ax1.set_xlabel("Month")
    ax1.set_ylabel("Average Advertising Spend")
    ax1.set_title("Advertising Spend Over Time by Channel")
    ax1.legend()
    ax1.grid(True)
    plt.xticks(rotation=45)
    plt.show()

    plots["advertising_spend_by_channel"] = fig1

    # Plot 2
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    for channel in df_advertising["Advertising_Channel"].unique():
        subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
        ax2.plot(subset["Month"], subset["avg_registrations"], marker='o', label=channel)

    ax2.set_xlabel("Month")
    ax2.set_ylabel("Average Registrations")
    ax2.set_title("Registrations Over Time by Channel")
    ax2.legend()
    ax2.grid(True)
    plt.xticks(rotation=45)
    plt.show()

    plots["registrations_by_channel"] = fig2

    return plots



def calc_roi_per_channel(df: pd.DataFrame, conn):

    df.to_sql("game", conn, if_exists="replace", index=False)

    query_monthly = """WITH RankedData AS (
               SELECT
                   Advertising_Channel,
                   strftime('%Y-%m', Registration_Date) AS Month,
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
               WHERE Advertising_Channel <> 'Organic'
               GROUP BY Advertising_Channel, Month
           )
           SELECT
               Advertising_Channel,
               Month,
               ROI_7, ROI_30, ROI_60, ROI_90, ROI_120, ROI_150, ROI_180,
               RANK() OVER (PARTITION BY Month ORDER BY total_ad_spend DESC) AS Rank_Ad_Spend,
               RANK() OVER (PARTITION BY Month ORDER BY total_registrations DESC) AS Rank_Registrations
           FROM RankedData
           ORDER BY Month, Rank_Ad_Spend;"""

    query_overall = """WITH RankedData AS (
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
               WHERE Advertising_Channel <> 'Organic'
               GROUP BY Advertising_Channel
           )
           SELECT
               Advertising_Channel,
               ROI_7, ROI_30, ROI_60, ROI_90, ROI_120, ROI_150, ROI_180,
               RANK() OVER (ORDER BY total_ad_spend DESC) AS Rank_Ad_Spend,
               RANK() OVER (ORDER BY total_registrations DESC) AS Rank_Registrations
           FROM RankedData
           ORDER BY Rank_Ad_Spend;"""

    df_roi_by_month = pd.read_sql(query_monthly, conn)
    df_roi_overall = pd.read_sql(query_overall, conn)

    return df_roi_by_month, df_roi_overall



# def plot_all_channels_side_by_side(df_advertising: pd.DataFrame):
#     channels = df_advertising["Advertising_Channel"].unique()
#     num_channels = len(channels)
#
#     rows = num_channels
#     cols = 2
#     fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(15, 5 * rows), sharex=True)
#
#     for idx, channel in enumerate(channels):
#         subset = df_advertising[df_advertising["Advertising_Channel"] == channel]
#
#         axes[idx, 0].plot(subset["Month"], subset["avg_ad_spend"], marker='o', linestyle='-', color="blue")
#         axes[idx, 0].set_title(f"Ad Spend - {channel}")
#         axes[idx, 0].set_ylabel("Avg Ad Spend")
#         axes[idx, 0].grid(True)
#
#         axes[idx, 1].plot(subset["Month"], subset["avg_registrations"], marker='o', linestyle='-', color="green")
#         axes[idx, 1].set_title(f"Registrations - {channel}")
#         axes[idx, 1].set_ylabel("Avg Registrations")
#         axes[idx, 1].grid(True)
#
#     plt.xticks(rotation=0)
#     plt.tight_layout()
#     plt.show()


def plot_all_channels_side_by_side(df_advertising: pd.DataFrame):
    """יוצר גרף עם כל הערוצים זה לצד זה"""
    channels = df_advertising["Advertising_Channel"].unique()
    num_channels = len(channels)

    fig, axes = plt.subplots(nrows=num_channels, ncols=2, figsize=(15, 5 * num_channels), sharex=True)

    for idx, channel in enumerate(channels):
        subset = df_advertising[df_advertising["Advertising_Channel"] == channel]

        axes[idx, 0].plot(subset["Month"], subset["avg_ad_spend"], marker='o', linestyle='-', color="blue")
        axes[idx, 0].set_title(f"Ad Spend - {channel}")
        axes[idx, 0].set_ylabel("Avg Ad Spend")
        axes[idx, 0].grid(True)

        axes[idx, 1].plot(subset["Month"], subset["avg_registrations"], marker='o', linestyle='-', color="green")
        axes[idx, 1].set_title(f"Registrations - {channel}")
        axes[idx, 1].set_ylabel("Avg Registrations")
        axes[idx, 1].grid(True)

    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

    return {"all_channels_side_by_side": fig}