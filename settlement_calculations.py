def calculate_total_settlement_price(hourly_shaping_factor, day_ahead_applicable_index_price):
    """
    Calculate the Total Settlement Price based on the given formula.

    Parameters:
    hourly_shaping_factor (float): The shaping factor for the hour.
    day_ahead_applicable_index_price (float): The Day-Ahead Applicable Index Price in $/MWh.

    Returns:
    float: The Total Settlement Price in $/MWh.
    """
    # Step 1: Calculate the intermediate price
    intermediate_price = hourly_shaping_factor * day_ahead_applicable_index_price * 1.10

    # Step 2: Cap the intermediate price to the maximum of $2000/MWh
    capped_price = min(intermediate_price, 2000)

    # Step 3: Ensure the price is not lower than $0/MWh
    total_settlement_price = max(capped_price, 0)

    return total_settlement_price


def calculate_declined_energy_settlement_price(total_settlement_price, real_time_applicable_index_price):
    """
    Calculate the Declined Energy Settlement Price based on the given formula.

    Parameters:
    total_settlement_price (float): The Total Settlement Price in $/MWh.
    real_time_applicable_index_price (float): The Real-Time Applicable Index Price in $/MWh.

    Returns:
    float: The Declined Energy Settlement Price in $/MWh.
    """
    return min(0.8 * total_settlement_price, real_time_applicable_index_price)


def calculate_holdback_settlement_price(total_settlement_price, declined_energy_settlement_price):
    """
    Calculate the Holdback Settlement Price based on the given formula.

    Parameters:
    total_settlement_price (float): The Total Settlement Price in $/MWh.
    declined_energy_settlement_price (float): The Declined Energy Settlement Price in $/MWh.

    Returns:
    float: The Holdback Settlement Price in $/MWh.
    """
    return total_settlement_price - declined_energy_settlement_price

# Example usage
if __name__ == "__main__":

    hourly_shaping_factor = 1.2  # Example value
    day_ahead_applicable_index_price = 50.0  # Example value in $/MWh
    real_time_applicable_index_price = 60.0  # Example value in $/MWh

    total_price = calculate_total_settlement_price(hourly_shaping_factor, day_ahead_applicable_index_price)
    declined_price = calculate_declined_energy_settlement_price(total_price, real_time_applicable_index_price)
    holdback_price = calculate_holdback_settlement_price(total_price, declined_price)

    print(f"Total Settlement Price: {total_price} $/MWh")
    print(f"Declined Energy Settlement Price: {declined_price} $/MWh")
    print(f"Holdback Settlement Price: {holdback_price} $/MWh")
