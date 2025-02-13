import pandas as pd
import sqlite3
import os
from func import reformat_date, calc_df_avg_Depositors_by_country, avg_depositors_graph, calc_avg_deposits_df, calc_df_avg_Depositors_by_channel, calc_df_advertising_by_date, calc_advertising_by_channel_graphs, calc_roi_per_channel, plot_all_channels_side_by_side, save_outputs


input_file = os.environ.get('input_file')
output_dir = os.environ.get('output_dir')


df = pd.read_csv(input_file)
df = reformat_date(df)

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



plots_dict = {
    "plt_spend_end_registration_all_channels_combined": lambda: calc_advertising_by_channel_graphs(df_advertising),
    "plt_spend_end_registration_all_channels_side_by_side": lambda: plot_all_channels_side_by_side(df_advertising),
    "plt_avg_number_depositors_by_country": lambda: avg_depositors_graph(df_avg_number_Depositors_by_country, count=True, by=True),
    "plt_avg_amount_depositors_by_country": lambda: avg_depositors_graph(df_avg_depositors_amount_by_country, count=False, by=True),
    "plt_avg_number_depositors_by_chanel": lambda: avg_depositors_graph(df_avg_number_Depositors_by_channel, count=True, by=False),
    "plt_avg_amount_depositors_by_chanel": lambda: avg_depositors_graph(df_avg_depositors_amount_by_channel, count=False, by=False)
}


all_plots = {}
for key, func in plots_dict.items():
    all_plots.update(func())

save_outputs(output_dir, dataframes_dict, all_plots)


print("Thank you very much")