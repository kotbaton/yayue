import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()   # settings for seaborn plotting style

# directories with data-files for the generated Figures (default: current dir)
data_dir = './Data/'  # work-default: sub-directory of the sources
fig_dir = './Figs2/'  # will be created if it does not exist
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir, mode=0o755)

# data files
us_infl = data_dir + 'us_inf.csv'
# historical US inflation indices relative to 2020
df_mult = pd.read_csv(us_infl, comment='#')   # years as column more convinient than as index
print('US inflation (relative to 2020 prices) read from: ', us_infl)
# print(df_mult.describe())

wti_file = data_dir + 'oilPrices1.csv'    # csv cols: Number, Date, Brent, WTI
df = pd.read_csv(wti_file, index_col='Date', parse_dates=True)   # df-cols: Number, Brent, WTI
df_sel = df.iloc[:, [0, 2]]  # select Number and WTI cols
df_sel.insert(2, 'scale', '1.2', True)  # place-holder for price-scaling coef.
df_sel = df_sel.drop('Number', axis=1, inplace=False)     # column not needed but used for creating a df
df_clean = df_sel.dropna()      # drop rows with undefined WTI prices
df_clean.insert(2, 'WTI2020', '1.0', True)       # place-holder for constant 2020USD prices
print('WTI current (in USD) prices read from: ', wti_file)
#  print(df_clean.describe())

# linear appr. of price-scaling for defined prices (NaN dropped above)
cur_yr = 0
mult_start = mult_end = 0
for row in df_clean.index:
    year = row.year
    if cur_yr != year:
        cur_yr = year
        mrow1 = df_mult.loc[df_mult['year'] == cur_yr]['multip']
        mult_start = mrow1.iloc[0]
        next_yr = year + 1
        mrow2 = df_mult.loc[df_mult['year'] == next_yr]['multip']
        mult_end = mrow2.iloc[0]
    day_of_yr = row.day_of_year
    delta = mult_start - mult_end
    mult = mult_start - delta * day_of_yr / 365     # multiplier for the current day
    wti = df_clean['WTI'][row]
    wti2020 = mult * wti
    df_clean.at[row, 'scale'] = round(mult, 2)
    df_clean.at[row, 'WTI2020'] = round(wti2020, 2)

# aggregate WTI (i.e., current) prices
daily = df_clean['WTI'].resample('D').sum()
weekly = df_clean['WTI'].resample('W').sum()
monthly = df_clean['WTI'].resample('M').sum()
yearly = df_clean['WTI'].resample('Y').sum()
weekly = weekly.apply(lambda x: x/7)        # scale the sums by the corresponding number of days
monthly = monthly.apply(lambda x: x/30)
yearly = yearly.apply(lambda x: x/365)
# aggregate WTI2020 (i.e., WTI in constant 2020 USD) prices
daily20 = df_clean['WTI2020'].resample('D').sum()
weekly20 = df_clean['WTI2020'].resample('W').sum()
monthly20 = df_clean['WTI2020'].resample('M').sum()
yearly20 = df_clean['WTI2020'].resample('Y').sum()
weekly20 = weekly20.apply(lambda x: x/7)        # scale the sums by the corresponding number of days
monthly20 = monthly20.apply(lambda x: x/30)
yearly20 = yearly20.apply(lambda x: x/365)

# Make Figures with Time-series, KDE, and eCDF
# fig1: two plots with time series: of WTI and WTI2020
fig1 = plt.figure(figsize=(10, 8))
fig1.canvas.set_window_title('Time series of WTI oil prices')   # title of the window/canvas
fig1.subplots_adjust(wspace=0.3, hspace=0.5)

# current WTI prices, one plot with: daily, weekly, monthly, and yearly aggregations
ax1 = fig1.add_subplot(211)  # per-col, per_row, subplot numebr (starts from 1)
daily.plot(color='lightgreen', label='daily', ax=ax1)
weekly.plot(color='blue', label='weekly', ax=ax1)
monthly.plot(color='magenta', label='monthly', ax=ax1)
yearly.plot(color='darkred', label='yearly', ax=ax1)
ax1.set_xlabel('')
ax1.set_ylabel('Current USD prices')
ax1.set_title('Time series of WTI current USD prices')
ax1.legend(loc='upper left')

# 4 plots with WTI2020 (constant 2020USD) prices
# WRI2020: WTI prices in 2020 USD, one plot with: daily, weekly, monthly, and yearly aggregations
ax2 = fig1.add_subplot(212)
daily20.plot(color='lightgreen', label='daily', ax=ax2)
weekly20.plot(color='blue', label='weekly', ax=ax2)
monthly20.plot(color='magenta', label='monthly', ax=ax2)
yearly20.plot(color='darkred', label='yearly', ax=ax2)
df_clean['scale'].plot(color='darkgreen', label='scaling', secondary_y=True, ax=ax2)    # label ignored
ax2.set_xlabel('')
ax2.set_ylabel('Constant (2020USD) prices')
ax2.right_ax.set_ylabel('Daily scaling coef. to 2020USD prices')
ax2.set_title('Time series of WTI constant (2020USD) prices')
ax2.legend(loc='upper right')    # ax2.legend(loc='upper center')


# fig2: KDE & eCDF, 4 plots (generated by rows) for daily, weekly, monthly, yearly prices
fig2 = plt.figure(figsize=(18, 8))
fig2.canvas.set_window_title('Kernel density estimation and Empirical cumulative distribution')
fig2.subplots_adjust(wspace=0.3, hspace=0.5)
fig2.suptitle('Kernel density estimation (KDE) and Empirical cumulative distribution function (eCDF)')

# color palette. Note: set invalid parameter to get the long list of available palettes
# palettes good for 4 colors: Dark2, cividis, CMRmap, gnuplot, Set1, viridis
c1, c2, c3, c4 = sns.color_palette('Set1', 4)  # best for 4 colors: either Dark2 or Set1

# first plot: daily prices, twin axis ax3, ax3a
ax3 = fig2.add_subplot(221)  # per-col, per_row, subplot numebr (starts from 1)
ax3a = plt.twinx()
ax3a.grid(False)
ax3.set(xlim=(-25, 150))
sns.kdeplot(daily, label='KDE WTI', color=c1, ax=ax3)
sns.kdeplot(daily20, label='KDE WTI2020', color=c2, ax=ax3)
# sns.kdeplot(daily, label='WTI, adj 0.7', bw_adjust=0.7, color='magenta', ax=ax3)
# sns.kdeplot(daily, label='WTI, adj 0.5', bw_adjust=0.5, color='red', ax=ax3)  # adj 0.9 marginal change
# sns.kdeplot(daily, label='WTI, adj 0.1', bw_adjust=0.1, color='darkred', ax=ax3)  # adj 0.1 dominating change
# bw_method change only marginal
# sns.kdeplot(daily20, label='WTI2020, bw_method', bw_method='silverman', color='darkred', ax=ax3)  # bw_method='scott'
sns.kdeplot(daily, cumulative=True, label='eCDF WTI', color=c3, ax=ax3a)    # eCDF
sns.kdeplot(daily20, cumulative=True, label='eCDF WTI2020', color=c4, ax=ax3a)
# labels, legend, title
ax3.set_xlabel('Daily prices')
ax3.set_ylabel('KDE density')
ax3a.set_ylabel('eCDF density')
ax3.set_title('Daily WTI and WTI2020 prices')
hand1, lab1 = ax3.get_legend_handles_labels()
hand2, lab2 = ax3a.get_legend_handles_labels()
ax3.legend(loc='center right', handles=hand1+hand2, labels=lab1+lab2)

# second plot: weekly prices, twin axis ax4 and ax4a
ax4 = fig2.add_subplot(222)  # per-col, per_row, subplot numebr (starts from 1)
ax4a = plt.twinx()
ax4a.grid(False)
ax4.set(xlim=(-25, 150))
sns.kdeplot(weekly, label='KDE WTI', color=c1, ax=ax4)
sns.kdeplot(weekly20, label='KDE WTI2020', color=c2, ax=ax4)
sns.kdeplot(weekly, cumulative=True, label='eCDF WTI', color=c3, ax=ax4a)   # eCDF
sns.kdeplot(weekly20, cumulative=True, label='eCDF WTI2020', color=c4, ax=ax4a)
# labels, legend, title
ax4.set_xlabel('Weekly prices')
ax4.set_ylabel('KDE density')
ax4a.set_ylabel('eCDF density')
ax4.set_title('Weekly WTI and WTI2020 prices')
hand1, lab1 = ax4.get_legend_handles_labels()
hand2, lab2 = ax4a.get_legend_handles_labels()
ax4.legend(loc='center right', handles=hand1+hand2, labels=lab1+lab2)

# third plot: monthly prices; twin axis ax5 and ax5a
ax5 = fig2.add_subplot(223)  # per-col, per_row, subplot numebr (starts from 1)
ax5a = plt.twinx()
ax5a.grid(False)
ax5.set(xlim=(-25, 150))
sns.kdeplot(monthly, label='KDE WTI', color=c1, ax=ax5)
sns.kdeplot(monthly20, label='KDE WTI2020', color=c2, ax=ax5)
sns.kdeplot(monthly, cumulative=True, label='eCDF WTI', color=c3, ax=ax5a)
sns.kdeplot(monthly20, cumulative=True, label='eCDF WTI2020', color=c4, ax=ax5a)
# labels, legend, title
ax5.set_xlabel('Monthly prices')
ax5.set_ylabel('KDE density')
ax5a.set_ylabel('eCDF density')
ax5.set_title('Monthly WTI and WTI2020 prices')
hand1, lab1 = ax5.get_legend_handles_labels()
hand2, lab2 = ax5a.get_legend_handles_labels()
ax5.legend(loc='center right', handles=hand1+hand2, labels=lab1+lab2)

# fourth plot: yearly prices; twin axis ax6 and ax6a
ax6 = fig2.add_subplot(224)  # per-col, per_row, subplot numebr (starts from 1)
ax6a = plt.twinx()
ax6a.grid(False)
ax6.set(xlim=(-25, 150))
sns.kdeplot(monthly, label='KDE WTI', color=c1, ax=ax6)
sns.kdeplot(monthly20, label='KDE WTI2020', color=c2, ax=ax6)
sns.kdeplot(monthly, cumulative=True, label='eCDF WTI', color=c3, ax=ax6a)
sns.kdeplot(monthly20, cumulative=True, label='eCDF WTI2020', color=c4, ax=ax6a)
# labels, legend, title
ax6.set_xlabel('Yearly prices')
ax6.set_ylabel('KDE density')
ax6a.set_ylabel('eCDF density')
ax6.set_title('Yearly WTI and WTI2020 prices')
hand1, lab1 = ax6.get_legend_handles_labels()
hand2, lab2 = ax6a.get_legend_handles_labels()
ax6.legend(loc='center right', handles=hand1+hand2, labels=lab1+lab2)

# store and show Figs
fname1 = fig_dir + 'timeSeries.png'
fig1.savefig(fname1)  # bbox_inches='tight' param ignored
fname2 = fig_dir + 'kdeEcdf.png'
fig2.savefig(fname2)
print('Figures (TimeSeries, KDE, eCDF) saved to: ' + fname1 + ' and ' + fname2)
plt.show()
