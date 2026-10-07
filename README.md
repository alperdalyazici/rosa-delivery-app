# Rosa's Delivery Promise Optimizer

A Streamlit app that uses the deterministic delivery-time simulation and net
profit calculation from `Part1andPart2.ipynb` to recommend a promise for a
selected zone and time block.

## Run locally

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

The app starts with the notebook's default test range (20–80 minutes in
5-minute steps), a $9.00 margin per order, 1.8 future orders lost per late
order, a $10.00 refund per late order, and random seed 1. Adjust the range and
cost assumptions, then select **Find best promised time** to compare the
estimated net profit and late-order rate for each candidate.
