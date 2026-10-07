from __future__ import annotations

import numpy as np
import streamlit as st
from starter import COSTS, TIME_BLOCKS, ZONES, delivery_times


SEED = 1


def get_times(promise: int, zone: str, time_block: str) -> np.ndarray:
    """Return the notebook's deterministic delivery-time simulation."""
    return delivery_times(zone, time_block, promise, seed=SEED)


def get_cost(costs: dict[str, float]) -> float:
    """Calculate the refund and expected future-margin cost of one late order."""
    return costs["refund"] + costs["churn_orders"] * costs["margin"]


def best_promise(
    zone: str,
    time_block: str,
    promises: list[int],
    costs: dict[str, float],
) -> tuple[dict[str, float | int], list[dict[str, float | int | bool]]]:
    """Score each candidate using the notebook's net-profit formula."""
    late_cost = get_cost(costs)
    results: list[dict[str, float | int | bool]] = []
    best_result: dict[str, float | int | bool] | None = None

    for promise in promises:
        times = get_times(promise, zone, time_block)
        total = len(times)
        if total == 0:
            raise ValueError(
                f"The simulation returned no orders for {zone} / {time_block}."
            )

        late_count = int(np.sum(times > promise))
        profit = total * costs["margin"] - late_count * late_cost
        result: dict[str, float | int | bool] = {
            "Promise (minutes)": promise,
            "Net profit ($)": profit,
            "Late rate (%)": 100 * late_count / total,
            "Orders simulated": total,
            "Late orders": late_count,
            "Recommended": False,
        }
        results.append(result)

        if best_result is None or profit > best_result["Net profit ($)"]:
            best_result = result

    if best_result is None:
        raise ValueError("Choose a range that contains at least one promise time.")

    best_result["Recommended"] = True
    return best_result, results


st.set_page_config(page_title="Rosa | Promise Optimizer", page_icon="🚚", layout="wide")
st.title("Rosa's Delivery Promise Optimizer")
st.write(
    "Find the promised delivery time with the highest estimated net profit "
    "for a zone and time block."
)

with st.form("promise_optimizer"):
    zone_column, block_column = st.columns(2)
    with zone_column:
        zone = st.selectbox("Zone", options=ZONES)
    with block_column:
        time_block = st.selectbox("Time block", options=TIME_BLOCKS)

    st.subheader("Promise times to test")
    lower_column, upper_column, step_column = st.columns(3)
    with lower_column:
        lower_bound = st.number_input(
            "Shortest promise (minutes)",
            min_value=1,
            max_value=300,
            value=20,
            step=1,
        )
    with upper_column:
        upper_bound = st.number_input(
            "Longest promise (minutes)",
            min_value=1,
            max_value=300,
            value=80,
            step=1,
        )
    with step_column:
        step_size = st.number_input(
            "Step (minutes)", min_value=1, max_value=60, value=5, step=1
        )
    st.caption(
        "The range includes both endpoints; the longest promise is tested even "
        "when the step does not land on it."
    )

    st.subheader("Estimated order economics")
    margin_column, churn_column, refund_column = st.columns(3)
    with margin_column:
        margin = st.number_input(
            "Profit margin per order ($)",
            min_value=0.0,
            value=float(COSTS["margin"]),
            step=0.5,
            format="%.2f",
        )
    with churn_column:
        churn_orders = st.number_input(
            "Future orders lost per late order",
            min_value=0.0,
            value=float(COSTS["churn_orders"]),
            step=0.1,
            format="%.1f",
        )
    with refund_column:
        refund = st.number_input(
            "Refund cost per late order ($)",
            min_value=0.0,
            value=float(COSTS["refund"]),
            step=0.5,
            format="%.2f",
        )
    st.caption(
        "Estimated cost per late order = refund + (future orders lost × "
        "profit margin per order). The simulation uses the notebook's fixed "
        "random seed so results are reproducible."
    )

    submitted = st.form_submit_button(
        "Find best promised time", type="primary", use_container_width=True
    )

if submitted:
    if lower_bound > upper_bound:
        st.error("The shortest promise must be less than or equal to the longest.")
    else:
        promises = list(range(int(lower_bound), int(upper_bound) + 1, int(step_size)))
        if promises[-1] != int(upper_bound):
            promises.append(int(upper_bound))

        costs = {
            "margin": float(margin),
            "churn_orders": float(churn_orders),
            "refund": float(refund),
        }
        recommended, results = best_promise(zone, time_block, promises, costs)

        st.subheader(f"Recommendation · {zone} / {time_block}")
        result_column, profit_column, late_rate_column = st.columns(3)
        with result_column:
            st.metric("Promised delivery time", f'{recommended["Promise (minutes)"]} min')
        with profit_column:
            st.metric("Estimated net profit", f'${recommended["Net profit ($)"]:,.2f}')
        with late_rate_column:
            st.metric("Late-order rate", f'{recommended["Late rate (%)"]:.2f}%')

        st.caption(
            f'Based on {recommended["Orders simulated"]:,} simulated orders at '
            f'the recommended promise. Tested {len(promises)} promise times: '
            f'{", ".join(str(promise) for promise in promises)} minutes.'
        )
        st.dataframe(results, hide_index=True)
