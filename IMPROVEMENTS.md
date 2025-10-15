# Improvements & Notes

## ✅ Result Save Fix - COMPLETED (v1.5.0)
~~bug with old test data, fix save with date.~~

~~the problem is the code saves the results.json as default and reads it as default.~~

~~change it to save result by date-timestamp
and read from latest results, and keep max 5 results file.~~

**Status**: ✅ Implemented in version 1.5.0
- Results now saved with timestamp format: `best_results_YYYYMMDD_HH.json` (date + hour)
- ONE file per run (all algorithms/coins saved to same file)
- System automatically reads from latest results file
- Automatic cleanup keeps only 5 most recent result files
- See CHANGELOG.md for full details


## ✅ Algorithm Selection Menu - COMPLETED (v1.6.0)
**Status**: ✅ Implemented in version 1.6.0

Users can now choose which algorithm(s) to run at startup:
- **0**: Run ALL algorithms (default behavior)
- **1-8**: Run specific algorithm only (MACD, RSI, SUPPORT_VOLUME, VOL24, SMA, SCALPING, BOLLINGER_BANDS, STOCHASTIC)

This allows for faster testing when you want to focus on a specific algorithm without running all of them.

**Example usage:**
```
ALGORITHM SELECTION

Available algorithms:
  0. Run ALL algorithms
  1. MACD
  2. RSI
  3. SUPPORT_VOLUME
  4. VOL24
  5. SMA
  6. SCALPING
  7. BOLLINGER_BANDS
  8. STOCHASTIC

Enter your choice (0 for all, or 1-8 for specific algorithm): 2
✅ Running only: RSI
```
