import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
from func import reformat_date, calc_df_avg_Depositors_by_country, avg_depositors_graph, calc_avg_deposits_df, calc_df_avg_Depositors_by_channel, calc_df_advertising_by_date, calc_advertising_by_channel_graphs, calc_roi_per_channel, plot_all_channels_side_by_side, save_outputs


input_file = os.environ.get('input_file')
output_dir = os.environ.get('output_dir')


df = pd.read_csv(input_file)
df = reformat_date(df)
df.info()


df_number, df_amount = calc_avg_deposits_df(df)
with sqlite3.connect("df_number.db") as conn:
   df_avg_number_Depositors_by_country = calc_df_avg_Depositors_by_country(df_number, conn)
   df_avg_number_Depositors_by_channel = calc_df_avg_Depositors_by_channel(df_number, conn)


with sqlite3.connect("df_amount.db") as conn:
   df_avg_depositors_amount_by_country = calc_df_avg_Depositors_by_country(df_amount, conn)
   df_avg_depositors_amount_by_channel = calc_df_avg_Depositors_by_channel(df_amount, conn)


with sqlite3.connect("df_main.db") as conn:
   df_advertising = calc_df_advertising_by_date(df, conn)
   df_roi_by_month, df_roi_overall = calc_roi_per_channel(df, conn)


dataframes_dict = {
    "df_avg_number_Depositors_by_country": df_avg_number_Depositors_by_country,
    "df_avg_number_Depositors_by_channel": df_avg_number_Depositors_by_channel,
    "df_avg_depositors_amount_by_country": df_avg_depositors_amount_by_country,
    "df_avg_depositors_amount_by_channel": df_avg_depositors_amount_by_channel,
    "df_advertising": df_advertising,
    "df_roi_by_month": df_roi_by_month,
    "df_roi_overall": df_roi_overall
}



plot_all_channels_side_by_side(df_advertising)
calc_advertising_by_channel_graphs(df_advertising)
avg_depositors_graph(df_avg_number_Depositors_by_country, count=True, by=True)
avg_depositors_graph(df_avg_depositors_amount_by_country, count=False, by=True)
avg_depositors_graph(df_avg_number_Depositors_by_channel, count=True, by=False)
avg_depositors_graph(df_avg_depositors_amount_by_channel, count=False, by=False)


plots_dict = {
    "spend_end_registration_all_channels_combined": lambda: calc_advertising_by_channel_graphs(df_advertising),
    "spend_end_registration_all_channels_side_by_side": lambda: plot_all_channels_side_by_side(df_advertising),
    "avg_number_depositors_by_country_graph": lambda: avg_depositors_graph(df_avg_number_Depositors_by_country, count=True, by=True),
    "avg_amount_depositors_by_country_graph": lambda: avg_depositors_graph(df_avg_depositors_amount_by_country, count=False, by=True),
    "avg_number_depositors_by_chanel_graph": lambda: avg_depositors_graph(df_avg_number_Depositors_by_channel, count=True, by=False),
    "avg_amount_depositors_by_chanel_graph": lambda: avg_depositors_graph(df_avg_depositors_amount_by_channel, count=False, by=False)
}

save_outputs(output_dir, dataframes_dict, plots_dict)


print('test1')





#
#
#
#
#
# df["Registration_Date"] = pd.to_datetime(df["Registration_Date"], dayfirst=True, errors="coerce")
# df["month"] = df["Registration_Date"].dt.month  # חילוץ החודש
#
#
# # יצירת סיכום חודשי לפי ערוץ פרסום
# df_monthly = df.groupby(["month", "Advertising_Channel"]).agg({
#    "Advertising_Spend": "mean",
#    "Number_Registrations": "mean",
#    "Accum_Day180_Deposit_Amount": "mean"
# }).reset_index()
#
#
# # המרת "month" לפורמט תאריך
# df_monthly["month"] = df_monthly["month"].astype(str)
#
#
# # הצגת 10 השורות הראשונות
# print(df_monthly.head())
#
#
#
#
#
#
# # גרף 1 - הוצאות פרסום לפי חודש
# plt.figure(figsize=(10, 5))
# sns.lineplot(data=df_monthly, x="month", y="Advertising_Spend", hue="Advertising_Channel", marker="o")
# plt.title("מגמת הוצאות פרסום לפי חודש וערוץ פרסום")
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()
#
#
# # גרף 2 - מספר הרשמות לפי חודש
# plt.figure(figsize=(10, 5))
# sns.lineplot(data=df_monthly, x="month", y="Number_Registrations", hue="Advertising_Channel", marker="o")
# plt.title("מגמת מספר הרשמות לפי חודש וערוץ פרסום")
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()
#
#
# # גרף 3 - הפקדות לאחר 180 יום לפי חודש
# plt.figure(figsize=(10, 5))
# sns.lineplot(data=df_monthly, x="month", y="Accum_Day180_Deposit_Amount", hue="Advertising_Channel", marker="o")
# plt.title("מגמת רווחיות (הפקדות) לפי חודש וערוץ פרסום")
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()
#
#
#
#
#
#
# # חישוב השינוי היחסי מהחודש הקודם
# df_monthly["ad_spend_change"] = df_monthly.groupby("Advertising_Channel")["Advertising_Spend"].pct_change()
# df_monthly["registrations_change"] = df_monthly.groupby("Advertising_Channel")["Number_Registrations"].pct_change()
# df_monthly["deposits_change"] = df_monthly.groupby("Advertising_Channel")["Accum_Day180_Deposit_Amount"].pct_change()
#
#
# # הצגת חודשים עם ירידות/עליות קיצוניות
# df_monthly[(df_monthly["ad_spend_change"].abs() > 0.3) |
#           (df_monthly["registrations_change"].abs() > 0.3) |
#           (df_monthly["deposits_change"].abs() > 0.3)]
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # Aggregate Data by Month
# df["Month"] = df["Registration_Date"].dt.to_period("M")  # Group by month
# monthly_trends = df.groupby("Month").agg({
#    "Number_Registrations": "sum",
#    "Advertising_Spend": "sum",
#    "Number_Day7_Depositors": "sum",
#    "Number_Day30_Depositors": "sum",
#    "Accum_Day30_Deposit_Amount": "sum"
# }).reset_index()
#
#
# # Convert Period to Datetime for plotting
# monthly_trends["Month"] = monthly_trends["Month"].astype(str)
# monthly_trends["Month"] = pd.to_datetime(monthly_trends["Month"])
#
#
# # Plot Trends
# plt.figure(figsize=(12, 6))
# sns.lineplot(data=monthly_trends, x="Month", y="Number_Registrations", label="Registrations", marker="o")
# sns.lineplot(data=monthly_trends, x="Month", y="Number_Day30_Depositors", label="Day30 Depositors", marker="s")
# sns.lineplot(data=monthly_trends, x="Month", y="Advertising_Spend", label="Ad Spend", marker="D")
#
#
# plt.axvline(pd.to_datetime("2023-09-01"), color="red", linestyle="--", label="Potential Change Point")
# plt.axvline(pd.to_datetime("2023-04-01"), color="blue", linestyle="--", label="Another Change Point")
#
#
# plt.xlabel("Month")
# plt.ylabel("Values (Scaled)")
# plt.title("Trend Analysis of Registrations, Deposits & Advertising Spend")
# plt.legend()
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()
#
#
# # Detect Monthly Percentage Changes
# monthly_trends["Reg_Change"] = monthly_trends["Number_Registrations"].pct_change() * 100
# monthly_trends["Dep_Change"] = monthly_trends["Number_Day30_Depositors"].pct_change() * 100
# monthly_trends["Ad_Change"] = monthly_trends["Advertising_Spend"].pct_change() * 100
#
#
# # Print Significant Changes (>10% increase or decrease)
# significant_changes = monthly_trends[
#    (monthly_trends["Reg_Change"].abs() > 10) |
#    (monthly_trends["Dep_Change"].abs() > 10) |
#    (monthly_trends["Ad_Change"].abs() > 10)
# ]
# print("\n🚀 Significant Trend Changes Detected:")
# print(significant_changes[["Month", "Reg_Change", "Dep_Change", "Ad_Change"]])






###############################
#               יש אנומליה רצינית כשמפרסמים בothe
#               צריך לראות מה קורה לממוצעי הוצאות על פרסום והכנסות מפרסום לפי כל הטבלא לפי ארצות הברית לופי השאר לפי חודשים#
# לבדוק הוצאות פרסום לפי ערוצים לאוך תקופת הזמן ולאולי יש ערוצים שפחות משקיעים בהן ולכן לאוך שזמן הכניסות שלהן יורדות ואולי יש ערוצם שכדאי להשקיע בהם יותר
#  בין פרסום לכניסות להשוות בין הוצאות פרסום לרישומים לאוך זמן ואולי להראות קשר


# אני אחשב את הערוץ הכי רווחי לאורך זמן ואז אעשה השווה בין הערוץ שעולה הכי הרבה לערוץ הכי רוחי
#                             #לבדוק מה הערוץ הכי יקר ולראות אם הוא גם הכי רווחי ואז לתת מסקנה שצריך להשקיע עוד בערץ הכי רווחי




# לבדוק קורלציה בין הערוץ הכי רווחי לערוץ הכי יציב


#                             #
#                             #
#                             #
#                             #
###############################


