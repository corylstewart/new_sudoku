class PriceRounding:
    #this class creates a adjusted value for the price of the option based on its greeks

    #a generic adjustment based on two values the sensitivity to those values and a value to be adjusted
    def value_adjustment(self, value1, value2, sensitivity, value_to_adjust):
        return value_to_adjust + (value2-value1) * sensitivity

    #adjusts the option value based on the change in stock price and the delta of the option
    def adjust_price_for_stock_price(self, stock_price, rounded_stock_price, delta, rounded_option_price):
        return self.value_adjustment(stock_price, rounded_stock_price, delta, rounded_option_price)

    #adjusts the option value based on the change in vol and the vega of the option
    def adjust_for_vol(self, vol, rounded_vol, vega, rounded_option_price):
        return self.value_adjustment(vol, rounded_vol, 100*vega, rounded_option_price)

    #adjusts the option value based on delta and vega
    def adjust_price_for_stock_price_and_vol(self, stock_price, rounded_stock_price, delta,
                                             vol, rounded_vol, vega, rounded_option_price):
        adjusted_for_stock = self.adjust_price_for_stock_price(stock_price, rounded_stock_price, delta, rounded_option_price)
        adjusted_for_vega = self.adjust_for_vol(vol, rounded_vol, vega, adjusted_for_stock)
        return adjusted_for_vega

    #round the price to the nearest nickel
    def round_stock_price(self, spot):
        return round(spot/.05)*.05

    #round vol to the nearest tenth
    def round_vol(self,vol):
        return round(vol/.01)*.01

    #round a dictionary of symbol/vol pairs
    def round_vol_dict(self, vol_dict):
        rounded_vol_dict = {}
        for symbol in vol_dict:
            rounded_vol_dict[symbol] = self.round_vol(vol_dict[symbol])
        return rounded_vol_dict